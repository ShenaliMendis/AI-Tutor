from fastapi import APIRouter, HTTPException, status
from app.models.v2.lesson import (
    LessonRequest, LessonResponse, ContentSection, 
    QuizRequest, QuizResponse, QuizQuestion
)
from app.models.v2.course import ResourceItem
from app.services.ai_service_v2 import AIServiceV2
from app.utils.id_generator import generate_id
import json
import re
import logging

# Configure logging
logger = logging.getLogger("course_generation_api")

router = APIRouter(tags=["lessons"])
ai_service = AIServiceV2()

# In-memory storage for lesson data
lesson_store = {}

# Reference to module store from modules.py
from app.api.v2.endpoints.modules import module_store

@router.post("/create-lesson-content", response_model=LessonResponse)
async def create_lesson_content(request: LessonRequest):
    # Get module information if available
    module_context = {}
    
    if request.module_id in module_store:
        module_context = module_store[request.module_id]
    else:
        # Use minimal context if module data is not available
        module_context = {
            "module_title": "Module",
            "module_summary": "Module summary not available",
        }
    
    # Prepare the prompt for lesson content creation
    prompt = ai_service.create_lesson_content_prompt(request, module_context)
    
    try:
        # Generate lesson content
        logger.info(f"Generating lesson content for: {request.lesson_title}")
        lesson_data = await ai_service.generate_ai_content(prompt, temperature=0.7)
        
        # Debug: Log a sample of the raw response
        logger.debug(f"Raw AI response (first 500 chars): {lesson_data[:500]}")
        
        # Clean and parse the response
        if "```" in lesson_data:
            json_match = re.search(r'```(?:json)?(.*?)```', lesson_data, re.DOTALL)
            if json_match:
                lesson_data = json_match.group(1).strip()
                logger.debug(f"Extracted JSON from code block: {lesson_data[:200]}...")
        
        # Parse the JSON with explicit error handling
        try:
            lesson_json = json.loads(lesson_data)
            logger.debug(f"Successfully parsed JSON: {json.dumps(lesson_json)[:200]}...")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Raw response: {lesson_data}")
            
            # Create a default JSON structure since parsing failed
            lesson_json = {
                "lesson_title": request.lesson_title,
                "introduction": f"Introduction to {request.lesson_title}.",
                "sections": [
                    {
                        "heading": "Main Concepts",
                        "content": "The AI model failed to generate proper content. Please try again.",
                        "importance": 1
                    }
                ],
                "summary": f"Summary of {request.lesson_title}.",
                "reflection_questions": ["What did you learn from this topic?"],
                "next_steps": "Continue to the next lesson."
            }
            logger.info("Using default lesson JSON structure due to parsing error")
        
        # Create default content for all required fields if missing
        lesson_defaults = {
            "lesson_title": request.lesson_title,
            "introduction": f"Introduction to {request.lesson_title}.",
            "sections": [{"heading": "Main Content", "content": "Content not available.", "importance": 1}],
            "summary": "Summary of key points covered in this lesson.",
            "reflection_questions": ["What did you learn from this lesson?"],
            "next_steps": "Continue to the next lesson."
        }
        
        # Fill in any missing fields with defaults
        for field, default_value in lesson_defaults.items():
            if field not in lesson_json or not lesson_json[field]:
                logger.warning(f"Missing or empty field in lesson response: {field}")
                lesson_json[field] = default_value
        
        # Validate sections structure
        if not isinstance(lesson_json["sections"], list) or len(lesson_json["sections"]) == 0:
            logger.error("Sections field is not a valid list or is empty")
            lesson_json["sections"] = [{"heading": "Main Content", "content": "Content not available.", "importance": 1}]
        
        # Process sections to ensure required fields
        processed_sections = []
        for i, section in enumerate(lesson_json["sections"]):
            section_defaults = {
                "heading": f"Section {i+1}",
                "content": "Content not available.",
                "importance": 1
            }
            
            # Create a new section dict with defaults for missing fields
            processed_section = {}
            for field, default_value in section_defaults.items():
                processed_section[field] = section.get(field, default_value)
                
                # If the field exists but is empty, use the default
                if field in section and not section[field]:
                    processed_section[field] = default_value
            
            processed_sections.append(ContentSection(**processed_section))
        
        # Validate reflection_questions is a list
        if not isinstance(lesson_json["reflection_questions"], list):
            logger.warning("reflection_questions is not a list, converting")
            if isinstance(lesson_json["reflection_questions"], str):
                lesson_json["reflection_questions"] = [lesson_json["reflection_questions"]]
            else:
                lesson_json["reflection_questions"] = ["What did you learn from this lesson?"]
        
        # Make sure reflection_questions is not empty
        if len(lesson_json["reflection_questions"]) == 0:
            lesson_json["reflection_questions"] = ["What did you learn from this lesson?"]
        
        # Process resources if available
        resources = None
        if "resources" in lesson_json and isinstance(lesson_json["resources"], list):
            try:
                resources = []
                for i, resource in enumerate(lesson_json["resources"]):
                    resource_defaults = {
                        "title": f"Resource {i+1}",
                        "description": "Additional learning resource",
                        "type": "reference",
                        "url": None
                    }
                    
                    # Create a new resource dict with defaults for missing fields
                    processed_resource = {}
                    for field, default_value in resource_defaults.items():
                        processed_resource[field] = resource.get(field, default_value)
                        
                        # If the field exists but is empty, use the default
                        if field in resource and not resource[field] and field != "url":
                            processed_resource[field] = default_value
                    
                    resources.append(ResourceItem(**processed_resource))
            except Exception as e:
                logger.warning(f"Error processing lesson resources: {str(e)}")
                resources = None
        
        # Create the response object with a unique ID
        lesson_id = generate_id("les")
        lesson_response = LessonResponse(
            lesson_id=lesson_id,
            lesson_title=lesson_json["lesson_title"],
            introduction=lesson_json["introduction"],
            sections=processed_sections,
            summary=lesson_json["summary"],
            reflection_questions=lesson_json["reflection_questions"],
            next_steps=lesson_json["next_steps"],
            resources=resources
        )
        
        # Store lesson context for quiz generation
        lesson_context_data = {
            "lesson_title": request.lesson_title,
            "lesson_objective": request.lesson_objective,
            "difficulty_level": request.difficulty_level.value if request.difficulty_level else None,
            "content_style": request.content_style.value if request.content_style else None
        }
        lesson_store[lesson_id] = lesson_context_data
        
        return lesson_response
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating lesson content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating lesson content: {str(e)}"
        )

@router.post("/create-quiz", response_model=QuizResponse)
async def create_quiz(request: QuizRequest):
    # Get lesson information if available
    lesson_context = {}
    
    if request.lesson_id in lesson_store:
        lesson_context = lesson_store[request.lesson_id]
    else:
        # Use minimal context if lesson data is not available
        lesson_context = {
            "lesson_title": "Lesson",
            "lesson_objective": "Lesson objective not available",
        }
    
    # Prepare the prompt for quiz creation
    prompt = ai_service.create_quiz_prompt(request, lesson_context)
    
    try:
        # Generate quiz
        logger.info(f"Generating quiz for lesson: {request.lesson_id}")
        quiz_data = await ai_service.generate_ai_content(prompt, temperature=0.7)
        
        # Debug: Log a sample of the raw response
        logger.debug(f"Raw AI response (first 500 chars): {quiz_data[:500]}")
        
        # Clean and parse the response
        if "```" in quiz_data:
            json_match = re.search(r'```(?:json)?(.*?)```', quiz_data, re.DOTALL)
            if json_match:
                quiz_data = json_match.group(1).strip()
                logger.debug(f"Extracted JSON from code block: {quiz_data[:200]}...")
        
        # Parse the JSON with explicit error handling
        try:
            quiz_json = json.loads(quiz_data)
            logger.debug(f"Successfully parsed JSON: {json.dumps(quiz_json)[:200]}...")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Raw response: {quiz_data}")
            
            # Create a default JSON structure since parsing failed
            quiz_json = {
                "quiz_introduction": f"Test your knowledge of {lesson_context.get('lesson_title', 'the lesson')}.",
                "questions": [
                    {
                        "question": "Default question since content generation failed?",
                        "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                        "correct_answer": "A. Option 1",
                        "explanation": "This is a default question because the AI failed to generate proper content.",
                        "difficulty": "medium"
                    }
                ],
                "passing_score": 80,
                "difficulty_level": request.difficulty_level.value if hasattr(request, 'difficulty_level') else "intermediate"
            }
            logger.info("Using default quiz JSON structure due to parsing error")
        
        # Create default content for all required fields if missing
        quiz_defaults = {
            "quiz_introduction": f"Test your knowledge of {lesson_context.get('lesson_title', 'the lesson')}.",
            "questions": [
                {
                    "question": "Default question since content generation failed?",
                    "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                    "correct_answer": "A. Option 1",
                    "explanation": "This is a default question because the AI failed to generate proper content.",
                    "difficulty": "medium"
                }
            ],
            "passing_score": 80,
            "difficulty_level": request.difficulty_level.value if hasattr(request, 'difficulty_level') else "intermediate"
        }
        
        # Fill in any missing fields with defaults
        for field, default_value in quiz_defaults.items():
            if field not in quiz_json or not quiz_json[field]:
                logger.warning(f"Missing or empty field in quiz response: {field}")
                quiz_json[field] = default_value
        
        # Validate questions structure
        if "questions" not in quiz_json or not isinstance(quiz_json["questions"], list) or len(quiz_json["questions"]) == 0:
            logger.error("Questions field is not a valid list or is empty")
            quiz_json["questions"] = quiz_defaults["questions"]
        
        # Process questions to ensure required fields
        questions_with_ids = []
        for i, question in enumerate(quiz_json["questions"]):
            question_defaults = {
                "question": f"Question {i+1}?",
                "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                "correct_answer": "A. Option 1",
                "explanation": "Explanation not provided.",
                "difficulty": "medium"
            }
            
            # Create a new question dict with defaults for missing fields
            processed_question = {}
            for field, default_value in question_defaults.items():
                processed_question[field] = question.get(field, default_value)
                
                # If the field exists but is empty, use the default
                if field in question and not question[field]:
                    processed_question[field] = default_value
            
            # Add question_id
            processed_question["question_id"] = generate_id("q")
            
            # Make sure options is a list
            if not isinstance(processed_question["options"], list) or len(processed_question["options"]) < 2:
                processed_question["options"] = question_defaults["options"]
            
            # Verify correct_answer is in options
            if processed_question["correct_answer"] not in processed_question["options"]:
                processed_question["correct_answer"] = processed_question["options"][0]
            
            questions_with_ids.append(QuizQuestion(**processed_question))
        
        # Create the response object with a unique ID
        quiz_id = generate_id("quiz")
        quiz_response = QuizResponse(
            quiz_id=quiz_id,
            lesson_id=request.lesson_id,
            quiz_introduction=quiz_json["quiz_introduction"],
            questions=questions_with_ids,
            passing_score=quiz_json.get("passing_score", 80),
            difficulty_level=quiz_json.get("difficulty_level", request.difficulty_level.value if hasattr(request, 'difficulty_level') else "intermediate")
        )
        
        return quiz_response
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quiz: {str(e)}"
        )
