from fastapi import APIRouter, HTTPException, FastAPI, Depends, BackgroundTasks, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
import os
import uuid
import json
import time
from datetime import datetime
from enum import Enum
import logging
from functools import lru_cache

# Advanced AI capabilities
from google.generativeai import GenerativeModel
import google.generativeai as genai
from dotenv import load_dotenv
import redis.asyncio as redis
import asyncio
import markdown
import re
from tenacity import retry, stop_after_attempt, wait_exponential

router = APIRouter(prefix="/api/v2", tags=["v2"])


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("course_generation_api")

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
CACHE_EXPIRY = int(os.getenv("CACHE_EXPIRY", 3600 * 24))  # Default: 24 hours

if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY environment variable not set")
    raise ValueError("GOOGLE_API_KEY environment variable must be set")

genai.configure(api_key=GOOGLE_API_KEY)


# ---------------

# Enums for structured input validation
class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentFormat(str, Enum):
    TEXT_HEAVY = "text-heavy"
    VISUAL = "visual"
    INTERACTIVE = "interactive"
    BALANCED = "balanced"

class ContentStyle(str, Enum):
    ACADEMIC = "academic"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    BUSINESS = "business"

class AssessmentType(str, Enum):
    QUIZ = "quiz"
    CASE_STUDY = "case_study"
    PROJECT = "project"
    REFLECTION = "reflection"
    MIXED = "mixed"

# Enhanced Data Models
class LearningObjective(BaseModel):
    objective: str
    importance: Optional[int] = Field(1, ge=1, le=5, description="Importance from 1-5")

class Prerequisite(BaseModel):
    description: str
    resource_link: Optional[str] = None

class CourseRequest(BaseModel):
    title: str
    description: str = Field(..., min_length=20)
    target_audience: str
    time_available: str
    learning_objectives: Optional[List[str]] = None
    preferred_format: Optional[ContentFormat] = ContentFormat.TEXT_HEAVY
    difficulty_level: Optional[DifficultyLevel] = DifficultyLevel.INTERMEDIATE
    content_style: Optional[ContentStyle] = ContentStyle.CONVERSATIONAL
    prerequisites: Optional[List[str]] = None
    industry_focus: Optional[str] = None
    assessment_preference: Optional[AssessmentType] = AssessmentType.QUIZ
    skills_to_develop: Optional[List[str]] = None
    include_resources: Optional[bool] = True
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Introduction to Artificial Intelligence",
                "description": "A comprehensive overview of AI concepts, applications, and ethical considerations",
                "target_audience": "University students with basic programming knowledge",
                "time_available": "4 weeks, 3 hours per week",
                "learning_objectives": [
                    "Understand key AI concepts and terminology",
                    "Recognize different AI approaches and their applications",
                    "Evaluate ethical implications of AI systems"
                ],
                "preferred_format": "balanced",
                "difficulty_level": "intermediate",
                "content_style": "academic", 
                "prerequisites": ["Basic Python knowledge", "Understanding of algorithms"],
                "industry_focus": "Technology",
                "assessment_preference": "mixed",
                "skills_to_develop": ["Critical thinking", "Problem solving", "Ethical reasoning"],
                "include_resources": True
            }
        }

class ResourceItem(BaseModel):
    title: str
    description: str
    type: str  # article, video, book, etc.
    url: Optional[str] = None

class ModuleInfo(BaseModel):
    module_id: str
    module_title: str
    module_summary: str
    estimated_duration: str
    key_concepts: List[str]

class CourseResponse(BaseModel):
    course_id: str
    course_title: str
    course_description: str
    course_introduction: str
    learning_outcomes: List[str]
    prerequisites: List[str]
    target_audience_description: str
    estimated_total_duration: str
    modules: List[ModuleInfo]
    recommended_resources: Optional[List[ResourceItem]] = None
    metadata: Dict[str, Any] = {}

class ModuleRequest(BaseModel):
    course_id: str
    module_title: str
    module_summary: str
    key_concepts: Optional[List[str]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    content_style: Optional[ContentStyle] = None

class ActivityInfo(BaseModel):
    activity_id: str
    activity_title: str
    activity_type: str
    activity_description: str
    estimated_duration: str

class LessonInfo(BaseModel):
    lesson_id: str
    lesson_title: str
    lesson_objective: str
    estimated_duration: str
    key_points: List[str]

class ModuleResponse(BaseModel):
    module_id: str
    module_introduction: str
    learning_path: str
    lessons: List[LessonInfo]
    activities: Optional[List[ActivityInfo]] = None
    resources: Optional[List[ResourceItem]] = None

class LessonRequest(BaseModel):
    module_id: str
    lesson_title: str
    lesson_objective: str
    difficulty_level: Optional[DifficultyLevel] = None
    content_style: Optional[ContentStyle] = None
    focus_areas: Optional[List[str]] = None
    
class ContentSection(BaseModel):
    heading: str
    content: str
    importance: int = 1

class LessonResponse(BaseModel):
    lesson_id: str
    lesson_title: str
    introduction: str
    sections: List[ContentSection]
    summary: str
    reflection_questions: List[str]
    next_steps: str
    resources: Optional[List[ResourceItem]] = None

class QuizQuestion(BaseModel):
    question_id: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    difficulty: str

class QuizRequest(BaseModel):
    lesson_id: str
    difficulty_level: Optional[DifficultyLevel] = DifficultyLevel.INTERMEDIATE
    num_questions: Optional[int] = Field(5, ge=3, le=10)
    include_explanations: Optional[bool] = True

class QuizResponse(BaseModel):
    quiz_id: str
    lesson_id: str
    quiz_introduction: str
    questions: List[QuizQuestion]
    passing_score: int
    difficulty_level: str
    
class FeedbackRequest(BaseModel):
    content_id: str  # Can be course_id, module_id, lesson_id, etc.
    content_type: str  # "course", "module", "lesson", "quiz"
    rating: int = Field(..., ge=1, le=5)
    feedback: str
    improvement_suggestions: Optional[str] = None

# Redis connection
@lru_cache()
async def get_redis():
    redis = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return redis

# Cache implementation
async def get_cached_response(redis, cache_key):
    cached_data = await redis.get(cache_key)
    if cached_data:
        logger.info(f"Cache hit for {cache_key}")
        return json.loads(cached_data)
    return None

async def set_cached_response(redis, cache_key, response_data, expiry=CACHE_EXPIRY):
    await redis.set(cache_key, json.dumps(response_data), ex=expiry)
    logger.info(f"Cached response for {cache_key}")

# Initialize AI models
@lru_cache()
def get_model(model_name=MODEL_NAME):
    try:
        logger.info(f"Initializing model: {model_name}")
        return GenerativeModel(model_name)
    except Exception as e:
        logger.error(f"Failed to initialize model: {str(e)}")
        raise RuntimeError(f"Failed to initialize AI model: {str(e)}")

# Helper function to generate unique IDs
def generate_id(prefix=""):
    timestamp = int(time.time())
    unique_id = f"{prefix}_{timestamp}_{uuid.uuid4().hex[:8]}"
    return unique_id

# Retry decorator for API calls
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_ai_content(prompt, temperature=0.7):
    model = get_model()
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        return response.text
    except Exception as e:
        logger.error(f"AI generation error: {str(e)}")
        raise


# Advanced prompting functions
def create_course_planning_prompt(request: CourseRequest) -> str:
    objectives_text = "\n".join([f"- {obj}" for obj in request.learning_objectives]) if request.learning_objectives else "No specific objectives provided."
    prerequisites_text = "\n".join([f"- {prereq}" for prereq in request.prerequisites]) if request.prerequisites else "No specific prerequisites provided."
    skills_text = "\n".join([f"- {skill}" for skill in request.skills_to_develop]) if request.skills_to_develop else "No specific skills focus provided."
    
    return f"""
    As an expert curriculum designer with deep expertise in educational design and pedagogy, create a comprehensive, 
    well-structured course plan based on the following specifications:
    
    # COURSE SPECIFICATIONS
    TITLE: {request.title}
    DESCRIPTION: {request.description}
    TARGET AUDIENCE: {request.target_audience}
    TIME AVAILABLE: {request.time_available}
    DIFFICULTY LEVEL: {request.difficulty_level.value}
    PREFERRED FORMAT: {request.preferred_format.value}
    CONTENT STYLE: {request.content_style.value}
    INDUSTRY FOCUS: {request.industry_focus if request.industry_focus else "General"}
    ASSESSMENT PREFERENCE: {request.assessment_preference.value}
    
    # LEARNING OBJECTIVES
    {objectives_text}
    
    # PREREQUISITES
    {prerequisites_text}
    
    # SKILLS TO DEVELOP
    {skills_text}
    
    # INSTRUCTIONS
    Design a comprehensive course structure that follows best practices in instructional design:
    
    1. Begin with a refined, captivating course title that accurately reflects the content
    2. Create an engaging course description (3-5 sentences) that highlights the value proposition
    3. Write a compelling course introduction (2 paragraphs) that:
       - Establishes relevance and importance of the subject matter
       - Creates interest and motivation for the learner
       - Provides an overview of what will be covered
    4. List 4-7 clear, measurable learning outcomes that start with action verbs
    5. Develop a detailed target audience description
    6. Provide an accurate total time estimate for course completion
    7. Design 3-7 logical modules that cover the subject matter comprehensively
    
    For each module provide:
    - A clear, descriptive title
    - A concise summary (2-3 sentences)
    - Estimated time to complete
    - 3-5 key concepts covered
    
    If resources are requested, recommend 5-8 high-quality learning resources (books, articles, videos, etc.)
    that supplement the course material.
    
    Format the response as a structured JSON object with the following schema:
    ```
    {{
      "course_title": "...",
      "course_description": "...",
      "course_introduction": "...",
      "learning_outcomes": ["...", "...", ...],
      "prerequisites": ["...", "...", ...],
      "target_audience_description": "...",
      "estimated_total_duration": "...",
      "modules": [
        {{
          "module_title": "...",
          "module_summary": "...",
          "estimated_duration": "...",
          "key_concepts": ["...", "...", ...]
        }},
        ...
      ],
      "recommended_resources": [
        {{
          "title": "...",
          "description": "...",
          "type": "...",
          "url": "..."
        }},
        ...
      ]
    }}
    ```
    
    Ensure all content is original, accurate, educational, and aligns perfectly with the requested specifications.
    Focus on creating a logically sequenced, pedagogically sound learning journey.
    """

def create_module_planning_prompt(request: ModuleRequest, course_context: Dict) -> str:
    return f"""
    As an expert instructional designer specializing in module development, create a comprehensive, 
    well-structured module plan based on the following specifications:
    
    # COURSE CONTEXT
    COURSE TITLE: {course_context.get('course_title', 'N/A')}
    COURSE DESCRIPTION: {course_context.get('course_description', 'N/A')}
    TARGET AUDIENCE: {course_context.get('target_audience_description', 'N/A')}
    
    # MODULE SPECIFICATIONS
    MODULE TITLE: {request.module_title}
    MODULE SUMMARY: {request.module_summary}
    KEY CONCEPTS: {", ".join(request.key_concepts) if request.key_concepts else "Not specified"}
    DIFFICULTY LEVEL: {request.difficulty_level.value if request.difficulty_level else "Not specified"}
    CONTENT STYLE: {request.content_style.value if request.content_style else "Not specified"}
    
    # INSTRUCTIONS
    Design a detailed module structure that follows best practices in instructional design:
    
    1. Create a compelling module introduction (1-2 paragraphs) that:
       - Establishes relevance of this module within the larger course
       - Creates interest and motivation for the learner
       - Provides an overview of what will be covered
    2. Develop a clear learning path description explaining how concepts build upon each other
    3. Design 3-5 logical lessons that cover the module content comprehensively
    4. Include 1-3 engaging activities that reinforce the module's content
    
    For each lesson provide:
    - A clear, descriptive title
    - A specific learning objective
    - Estimated time to complete
    - 3-5 key points that will be covered
    
    For each activity provide:
    - A descriptive title
    - The activity type (discussion, exercise, project, reflection, etc.)
    - A brief description
    - Estimated time to complete
    
    Include 3-5 high-quality recommended resources that specifically support this module's content.
    
    Format the response as a structured JSON object with the following schema:
    ```
    {{
      "module_introduction": "...",
      "learning_path": "...",
      "lessons": [
        {{
          "lesson_title": "...",
          "lesson_objective": "...",
          "estimated_duration": "...",
          "key_points": ["...", "...", ...]
        }},
        ...
      ],
      "activities": [
        {{
          "activity_title": "...",
          "activity_type": "...",
          "activity_description": "...",
          "estimated_duration": "..."
        }},
        ...
      ],
      "resources": [
        {{
          "title": "...",
          "description": "...",
          "type": "...",
          "url": "..."  // Optional
        }},
        ...
      ]
    }}
    ```
    
    Ensure all content is educational, logically sequenced, and aligns with the module's purpose.
    Focus on creating clear conceptual connections between lessons and activities.
    """

def create_lesson_content_prompt(request: LessonRequest, module_context: Dict) -> str:
    focus_areas_text = ", ".join(request.focus_areas) if request.focus_areas else "Not specified"
    
    return f"""
    As an expert educational content developer with expertise in creating engaging and instructional lesson content,
    create a comprehensive lesson based on the following specifications:
    
    # MODULE CONTEXT
    MODULE TITLE: {module_context.get('module_title', 'N/A')}
    MODULE SUMMARY: {module_context.get('module_summary', 'N/A')}
    
    # LESSON SPECIFICATIONS
    LESSON TITLE: {request.lesson_title}
    LESSON OBJECTIVE: {request.lesson_objective}
    DIFFICULTY LEVEL: {request.difficulty_level.value if request.difficulty_level else "Not specified"}
    CONTENT STYLE: {request.content_style.value if request.content_style else "Not specified"}
    FOCUS AREAS: {focus_areas_text}
    
    # INSTRUCTIONS
    Create comprehensive, well-structured lesson content that effectively teaches the subject matter.
    Structure your lesson with the following components:
    
    1. An engaging introduction (1-2 paragraphs) that:
       - Creates interest in the topic
       - Connects to prior knowledge
       - Clearly states what will be learned
       
    2. 4-6 content sections, each with:
       - A descriptive heading
       - Clear explanations of concepts (200-400 words per section)
       - Examples, analogies, or case studies where appropriate
       - Visual descriptions or diagrams where helpful
       - A smooth transition to the next section
       
    3. A concise summary (1 paragraph) that:
       - Reinforces key takeaways
       - Connects back to the main learning objective
       
    4. 3-5 reflection questions that promote critical thinking
    
    5. Next steps guidance that suggests how to apply or extend the learning
    
    6. 2-4 recommended resources for further exploration
    
    Throughout the lesson:
    - Use clear, concise language appropriate for the difficulty level
    - Employ the specified content style consistently
    - Incorporate engaging elements like stories, questions, and real-world applications
    - Focus particularly on the specified focus areas
    - Ensure content is factually accurate and educationally sound
    
    Format the response as a structured JSON object with the following schema:
    ```
    {{
      "lesson_title": "...",
      "introduction": "...",
      "sections": [
        {{
          "heading": "...",
          "content": "...",
          "importance": 2  // 1-3 scale indicating importance of this section
        }},
        ...
      ],
      "summary": "...",
      "reflection_questions": ["...", "...", ...],
      "next_steps": "...",
      "resources": [
        {{
          "title": "...",
          "description": "...",
          "type": "...",
          "url": "..."  // Optional
        }},
        ...
      ]
    }}
    ```
    
    Ensure the content is original, thorough, educational, and precisely aligned with the learning objective.
    """

def create_quiz_prompt(request: QuizRequest, lesson_context: Dict) -> str:
    return f"""
    As an expert assessment designer with expertise in educational testing and evaluation,
    create a comprehensive quiz based on the following specifications:
    
    # LESSON CONTEXT
    LESSON TITLE: {lesson_context.get('lesson_title', 'N/A')}
    LESSON OBJECTIVE: {lesson_context.get('lesson_objective', 'N/A')}
    
    # QUIZ SPECIFICATIONS
    DIFFICULTY LEVEL: {request.difficulty_level.value}
    NUMBER OF QUESTIONS: {request.num_questions}
    INCLUDE EXPLANATIONS: {request.include_explanations}
    
    # INSTRUCTIONS
    Design a comprehensive assessment that effectively evaluates understanding of the lesson content.
    Create a quiz with the following elements:
    
    1. A brief quiz introduction that:
       - Explains the purpose of the assessment
       - Provides clear instructions for completion
       
    2. {request.num_questions} questions that:
       - Are directly aligned with the lesson objective
       - Test different cognitive levels (knowledge, comprehension, application, analysis)
       - Use a variety of question types (predominantly multiple choice for this format)
       - Increase in complexity throughout the quiz
       
    For each question provide:
    - A clear, unambiguous question prompt
    - 4 options (labeled A, B, C, D) with only one correct answer
    - The correct answer clearly indicated
    - A brief explanation of why the answer is correct (if explanations are requested)
    - A difficulty rating (easy, medium, hard)
    
    Set an appropriate passing score based on the quiz difficulty.
    
    Format the response as a structured JSON object with the following schema:
    ```
    {{
      "quiz_introduction": "...",
      "questions": [
        {{
          "question": "...",
          "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
          "correct_answer": "B. ...",
          "explanation": "...",
          "difficulty": "medium"
        }},
        ...
      ],
      "passing_score": 80, // percentage
      "difficulty_level": "{request.difficulty_level.value}"
    }}
    ```
    
    Ensure questions are clear, fair, educational, and directly assess the learning objectives.
    Focus on creating assessment items that truly measure understanding rather than just recall.
    """


# API v2 root endpoint
@router.get("/")
async def v2_root():
    """
    API v2 root endpoint - shows API information
    """
    return {
        "version": "2.0.0",
        "name": "AI Tutor API",
        "status": "In Development",
        "new_features": [
            "Enhanced course generation with more customization options",
            "Support for additional export formats (PDF, DOCX)",
            "User management and course sharing",
            "Analytics and progress tracking"
        ]
    }

@router.post("/plan-course", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def plan_course(
    request: CourseRequest,
    background_tasks: BackgroundTasks,
    redis: redis.Redis = Depends(get_redis)
):
    # Generate cache key based on request
    cache_key = f"course:{hash(frozenset({k: v for k, v in request.dict().items() if v is not None}.items()))}"
    
    # Check cache first
    cached_response = await get_cached_response(redis, cache_key)
    if cached_response:
        return cached_response
    
    # Prepare the prompt for course planning
    prompt = create_course_planning_prompt(request)
    
    try:
        # Generate course plan
        logger.info(f"Generating course plan for: {request.title}")
        course_data = await generate_ai_content(prompt, temperature=0.7)
        
        # Clean and parse the response
        if "```" in course_data:
            # Extract JSON from code blocks if present
            import re
            json_match = re.search(r'```(?:json)?(.*?)```', course_data, re.DOTALL)
            if json_match:
                course_data = json_match.group(1).strip()
        
        course_json = json.loads(course_data)
        
        # Add IDs to each module
        course_id = generate_id("course")
        modules_with_ids = []
        
        for module in course_json["modules"]:
            module_with_id = {
                "module_id": generate_id("mod"),
                "module_title": module["module_title"],
                "module_summary": module["module_summary"],
                "estimated_duration": module["estimated_duration"],
                "key_concepts": module["key_concepts"]
            }
            modules_with_ids.append(ModuleInfo(**module_with_id))
        
        # Prepare recommended resources if available
        recommended_resources = None
        if "recommended_resources" in course_json and request.include_resources:
            recommended_resources = [ResourceItem(**resource) for resource in course_json["recommended_resources"]]
        
        # Create the response object
        course_response = CourseResponse(
            course_id=course_id,
            course_title=course_json["course_title"],
            course_description=course_json["course_description"],
            course_introduction=course_json["course_introduction"],
            learning_outcomes=course_json["learning_outcomes"],
            prerequisites=course_json["prerequisites"],
            target_audience_description=course_json["target_audience_description"],
            estimated_total_duration=course_json["estimated_total_duration"],
            modules=modules_with_ids,
            recommended_resources=recommended_resources,
            metadata={
                "created_at": datetime.now().isoformat(),
                "difficulty_level": request.difficulty_level.value,
                "preferred_format": request.preferred_format.value,
                "content_style": request.content_style.value,
            }
        )
        
        # Cache the response
        background_tasks.add_task(
            set_cached_response, redis, cache_key, course_response.dict()
        )
        
        return course_response
    
    except Exception as e:
        logger.error(f"Error generating course: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error generating course: {str(e)}"
        )

@router.post("/plan-module", response_model=ModuleResponse)
async def plan_module(
    request: ModuleRequest,
    background_tasks: BackgroundTasks,
    redis: redis.Redis = Depends(get_redis)
):
    # Generate cache key
    cache_key = f"module:{hash(frozenset({k: v for k, v in request.dict().items() if v is not None}.items()))}"
    
    # Check cache first
    cached_response = await get_cached_response(redis, cache_key)
    if cached_response:
        return cached_response
    
    # Get course information if available
    course_key = f"course_data:{request.course_id}"
    course_data = await redis.get(course_key)
    course_context = {}
    
    if not course_data:
        # Use minimal context if course data is not available
        course_context = {
            "course_title": "Course",
            "course_description": "Course description not available",
            "target_audience_description": "Target audience not specified"
        }
    else:
        course_context = json.loads(course_data)
    
    # Prepare the prompt for module planning
    prompt = create_module_planning_prompt(request, course_context)
    
    try:
        # Generate module plan
        logger.info(f"Generating module plan for: {request.module_title}")
        module_data = await generate_ai_content(prompt, temperature=0.7)
        
        # Clean and parse the response
        if "```" in module_data:
            import re
            json_match = re.search(r'```(?:json)?(.*?)```', module_data, re.DOTALL)
            if json_match:
                module_data = json_match.group(1).strip()
        
        module_json = json.loads(module_data)
        
        # Add IDs to lessons and activities
        module_id = generate_id("mod")
        lessons_with_ids = []
        activities_with_ids = []
        
        for lesson in module_json["lessons"]:
            lesson_with_id = {
                "lesson_id": generate_id("les"),
                "lesson_title": lesson["lesson_title"],
                "lesson_objective": lesson["lesson_objective"],
                "estimated_duration": lesson["estimated_duration"],
                "key_points": lesson["key_points"]
            }
            lessons_with_ids.append(LessonInfo(**lesson_with_id))
        
        if "activities" in module_json:
            for activity in module_json["activities"]:
                activity_with_id = {
                    "activity_id": generate_id("act"),
                    "activity_title": activity["activity_title"],
                    "activity_type": activity["activity_type"],
                    "activity_description": activity["activity_description"],
                    "estimated_duration": activity["estimated_duration"]
                }
                activities_with_ids.append(ActivityInfo(**activity_with_id))
        
        # Prepare resources if available
        resources = None
        if "resources" in module_json:
            resources = [ResourceItem(**resource) for resource in module_json["resources"]]
        
        # Create the response object
        module_response = ModuleResponse(
            module_id=module_id,
            module_introduction=module_json["module_introduction"],
            learning_path=module_json["learning_path"],
            lessons=lessons_with_ids,
            activities=activities_with_ids if activities_with_ids else None,
            resources=resources
        )
        
        # Cache the response
        background_tasks.add_task(
            set_cached_response, redis, cache_key, module_response.dict()
        )
        
        # Store module context for lesson generation
        module_context_key = f"module_data:{module_id}"
        module_context_data = {
            "module_title": request.module_title,
            "module_summary": request.module_summary,
            "difficulty_level": request.difficulty_level.value if request.difficulty_level else None,
            "content_style": request.content_style.value if request.content_style else None
        }
        background_tasks.add_task(
            redis.set, module_context_key, json.dumps(module_context_data), ex=CACHE_EXPIRY
        )
        
        return module_response
    
    except Exception as e:
        logger.error(f"Error generating module: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating module: {str(e)}"
        )

@router.post("/create-quiz", response_model=QuizResponse)
async def create_quiz(
    request: QuizRequest,
    background_tasks: BackgroundTasks,
    redis: redis.Redis = Depends(get_redis)
):
    # Generate cache key
    cache_key = f"quiz:{hash(frozenset({k: v for k, v in request.dict().items() if v is not None}.items()))}"
    
    # Check cache first
    cached_response = await get_cached_response(redis, cache_key)
    if cached_response:
        return cached_response
    
    # Get lesson information if available
    lesson_key = f"lesson_data:{request.lesson_id}"
    lesson_data = await redis.get(lesson_key)
    lesson_context = {}
    
    if not lesson_data:
        # Use minimal context if lesson data is not available
        lesson_context = {
            "lesson_title": "Lesson",
            "lesson_objective": "Lesson objective not available",
        }
    else:
        lesson_context = json.loads(lesson_data)
    
    # Prepare the prompt for quiz creation
    prompt = create_quiz_prompt(request, lesson_context)
    
    try:
        # Generate quiz
        logger.info(f"Generating quiz for lesson: {request.lesson_id}")
        quiz_data = await generate_ai_content(prompt, temperature=0.7)
        
        # Clean and parse the response
        if "```" in quiz_data:
            import re
            json_match = re.search(r'```(?:json)?(.*?)```', quiz_data, re.DOTALL)
            if json_match:
                quiz_data = json_match.group(1).strip()
        
        quiz_json = json.loads(quiz_data)
        
        # Add IDs to questions
        questions_with_ids = []
        for question in quiz_json["questions"]:
            question_with_id = {
                "question_id": generate_id("q"),
                "question": question["question"],
                "options": question["options"],
                "correct_answer": question["correct_answer"],
                "explanation": question["explanation"] if request.include_explanations else "",
                "difficulty": question["difficulty"]
            }
            questions_with_ids.append(QuizQuestion(**question_with_id))
        
        # Create the response object with a unique ID
        quiz_id = generate_id("quiz")
        quiz_response = QuizResponse(
            quiz_id=quiz_id,
            lesson_id=request.lesson_id,
            quiz_introduction=quiz_json["quiz_introduction"],
            questions=questions_with_ids,
            passing_score=quiz_json["passing_score"],
            difficulty_level=quiz_json["difficulty_level"]
        )
        
        # Cache the response
        background_tasks.add_task(
            set_cached_response, redis, cache_key, quiz_response.dict()
        )
        
        return quiz_response
    
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quiz: {str(e)}"
        )

@router.post("/create-lesson-content", response_model=LessonResponse)
async def create_lesson_content(
    request: LessonRequest,
    background_tasks: BackgroundTasks,
    redis: redis.Redis = Depends(get_redis)
):
    # Generate cache key
    cache_key = f"lesson:{hash(frozenset({k: v for k, v in request.dict().items() if v is not None}.items()))}"
    
    # Check cache first
    cached_response = await get_cached_response(redis, cache_key)
    if cached_response:
        return cached_response
    
    # Get module information if available
    module_key = f"module_data:{request.module_id}"
    module_data = await redis.get(module_key)
    module_context = {}
    
    if not module_data:
        # Use minimal context if module data is not available
        module_context = {
            "module_title": "Module",
            "module_summary": "Module summary not available",
        }
    else:
        module_context = json.loads(module_data)
    
    # Prepare the prompt for lesson content creation
    prompt = create_lesson_content_prompt(request, module_context)
    
    try:
        # Generate lesson content
        logger.info(f"Generating lesson content for: {request.lesson_title}")
        lesson_data = await generate_ai_content(prompt, temperature=0.7)
        
        # Clean and parse the response
        if "```" in lesson_data:
            json_match = re.search(r'```(?:json)?(.*?)```', lesson_data, re.DOTALL)
            if json_match:
                lesson_data = json_match.group(1).strip()
        
        lesson_json = json.loads(lesson_data)
        
        # Create the response object with a unique ID
        lesson_id = generate_id("les")
        lesson_response = LessonResponse(
            lesson_id=lesson_id,
            lesson_title=lesson_json["lesson_title"],
            introduction=lesson_json["introduction"],
            sections=[ContentSection(**section) for section in lesson_json["sections"]],
            summary=lesson_json["summary"],
            reflection_questions=lesson_json["reflection_questions"],
            next_steps=lesson_json["next_steps"],
            resources=[ResourceItem(**resource) for resource in lesson_json["resources"]] if "resources" in lesson_json else None
        )
        
        # Cache the response
        background_tasks.add_task(
            set_cached_response, redis, cache_key, lesson_response.dict()
        )
        
        # Store lesson context for quiz generation
        lesson_context_key = f"lesson_data:{lesson_id}"
        lesson_context_data = {
            "lesson_title": request.lesson_title,
            "lesson_objective": request.lesson_objective,
            "difficulty_level": request.difficulty_level.value if request.difficulty_level else None,
            "content_style": request.content_style.value if request.content_style else None
        }
        background_tasks.add_task(
            redis.set, lesson_context_key, json.dumps(lesson_context_data), ex=CACHE_EXPIRY
        )
        
        return lesson_response
    
    except Exception as e:
        logger.error(f"Error generating lesson content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating lesson content: {str(e)}"
        )


# Advanced endpoints for enhanced functionality
@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks,
):
    """
    Store user feedback for content and use it to improve future generations
    """
    try:
        feedback_id = generate_id("feedback")
        feedback_data = {
            "feedback_id": feedback_id,
            "content_id": feedback.content_id,
            "content_type": feedback.content_type,
            "rating": feedback.rating,
            "feedback": feedback.feedback,
            "improvement_suggestions": feedback.improvement_suggestions,
            "timestamp": datetime.now().isoformat()
        }
        
        # In a real implementation, store this in a database
        logger.info(f"Received feedback: {feedback_data}")
        
        # Background task to analyze feedback and improve prompt templates
        # This would be implemented in a production system
        
        return {"status": "success", "feedback_id": feedback_id}
    
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )

@router.get("/export-course/{course_id}", status_code=status.HTTP_200_OK)
async def export_course(
    course_id: str,
    format: str = Query("md", description="Export format: md, html, pdf"),
    redis: redis.Redis = Depends(get_redis)
):
    """
    Export an entire course in various formats
    """
    try:
        # Get course data
        course_key = f"course_data:{course_id}"
        course_data = await redis.get(course_key)
        
        if not course_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID {course_id} not found"
            )
        
        # In a real implementation, we would fetch all modules, lessons, etc.
        # and generate the appropriate format
        
        # For now, return a simple confirmation
        return {
            "status": "success", 
            "message": f"Course export in {format} format will be available shortly",
            "course_id": course_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting course: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting course: {str(e)}"
        )

@router.post("/generate-learning-path", status_code=status.HTTP_201_CREATED)
async def generate_learning_path(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
):
    """
    Generate a personalized learning path based on user goals and current knowledge
    """
    try:
        # This would be fully implemented in a production system
        path_id = generate_id("path")
        
        return {
            "status": "success", 
            "path_id": path_id,
            "message": "Learning path generation started. Results will be available shortly."
        }
    
    except Exception as e:
        logger.error(f"Error generating learning path: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating learning path: {str(e)}"
        )

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Endpoint for monitoring system health
    """
    return {
        "status": "healthy",
        "api_version": "2.0.0",
        "model": MODEL_NAME,
        "timestamp": datetime.now().isoformat()
    }
