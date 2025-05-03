import json
from typing import Any, Dict
import google.generativeai as genai
from fastapi import HTTPException
from app.config import get_settings
import logging
import re
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_service_v2")

class AIServiceV2:
    def __init__(self):
        settings = get_settings()
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Initialize the model
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.model_name)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_ai_content(self, prompt: str, temperature=0.7) -> str:
        """Generate content using the AI model with retry logic"""
        try:
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json" # Request JSON format if supported
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Log a truncated version of the response for debugging
            response_preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
            logger.debug(f"AI response preview: {response_preview}")
            
            return response.text
        except Exception as e:
            logger.error(f"AI generation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")
    
    async def generate_structured_content(self, prompt: str) -> Dict[str, Any]:
        """Generate content and parse it as JSON"""
        try:
            response = await self.generate_ai_content(prompt)
            
            # Clean the response to extract JSON
            if "```" in response:
                json_match = re.search(r'```(?:json)?(.*?)```', response, re.DOTALL)
                if json_match:
                    response = json_match.group(1).strip()
                
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Invalid JSON response: {str(e)}")
    
    def create_course_planning_prompt(self, request) -> str:
        """Create a detailed prompt for course planning"""
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
        ASSESSMENT PREFERENCE: {request.assessment_preference.value if hasattr(request, 'assessment_preference') and request.assessment_preference else "quiz"}
        
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
        
        Format the response as a structured JSON object with EXACTLY this structure:
        ```json
        {{
          "course_title": "The title of the course",
          "course_description": "A comprehensive description of the course",
          "course_introduction": "An introduction to the course that spans multiple paragraphs",
          "learning_outcomes": [
            "Outcome 1: Learn something important",
            "Outcome 2: Master a specific skill",
            "Outcome 3: Apply knowledge in real-world contexts"
          ],
          "prerequisites": [
            "Prerequisite 1",
            "Prerequisite 2"
          ],
          "target_audience_description": "Detailed description of target audience",
          "estimated_total_duration": "X weeks, Y hours per week",
          "modules": [
            {{
              "module_title": "Title of Module 1",
              "module_summary": "Summary of what module 1 covers",
              "estimated_duration": "X hours",
              "key_concepts": [
                "Concept 1",
                "Concept 2",
                "Concept 3"
              ]
            }},
            {{
              "module_title": "Title of Module 2",
              "module_summary": "Summary of what module 2 covers",
              "estimated_duration": "Y hours",
              "key_concepts": [
                "Concept 1",
                "Concept 2",
                "Concept 3"
              ]
            }}
          ],
          "recommended_resources": [
            {{
              "title": "Resource Title",
              "description": "Brief description of the resource",
              "type": "book/article/video/website",
              "url": "http://example.com/resource"
            }}
          ]
        }}
        ```
        
        IMPORTANT: Follow the EXACT format above, with all required fields. Each module MUST have module_title, module_summary, estimated_duration, and key_concepts fields.
        """
    
    def create_module_planning_prompt(self, request, course_context: Dict) -> str:
        """Create a detailed prompt for module planning"""
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
        
        Format the response as a structured JSON object with EXACTLY this structure:
        ```json
        {{
          "module_introduction": "A compelling introduction to the module...",
          "learning_path": "Description of how the concepts build upon each other...",
          "lessons": [
            {{
              "lesson_title": "Title of Lesson 1",
              "lesson_objective": "Specific objective for lesson 1",
              "estimated_duration": "30-45 minutes",
              "key_points": [
                "Key point 1",
                "Key point 2",
                "Key point 3"
              ]
            }},
            {{
              "lesson_title": "Title of Lesson 2",
              "lesson_objective": "Specific objective for lesson 2",
              "estimated_duration": "45-60 minutes",
              "key_points": [
                "Key point 1",
                "Key point 2",
                "Key point 3"
              ]
            }}
          ],
          "activities": [
            {{
              "activity_title": "Title of Activity 1",
              "activity_type": "exercise",
              "activity_description": "Description of the activity",
              "estimated_duration": "20 minutes"
            }}
          ],
          "resources": [
            {{
              "title": "Resource Title",
              "description": "Description of the resource",
              "type": "book/article/video",
              "url": "http://example.com/resource"
            }}
          ]
        }}
        ```
        
        IMPORTANT: Follow the EXACT format above, with all required fields. Each lesson MUST include lesson_title, lesson_objective, estimated_duration, and key_points (as an array).
        """
    
    def create_lesson_content_prompt(self, request, module_context: Dict) -> str:
        """Create a detailed prompt for lesson content creation"""
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
        
        You MUST format the response as a valid JSON object with the following structure:
        {{
          "lesson_title": "{request.lesson_title}",
          "introduction": "An engaging introduction to the lesson...",
          "sections": [
            {{
              "heading": "First Section Heading",
              "content": "Detailed content for the first section...",
              "importance": 2
            }},
            {{
              "heading": "Second Section Heading",
              "content": "Detailed content for the second section...",
              "importance": 3
            }}
          ],
          "summary": "A concise summary of the lesson...",
          "reflection_questions": [
            "First reflection question?",
            "Second reflection question?",
            "Third reflection question?"
          ],
          "next_steps": "Guidance on how to apply or extend the learning...",
          "resources": [
            {{
              "title": "Resource Title",
              "description": "Description of the resource",
              "type": "book/article/video",
              "url": "http://example.com/resource"
            }}
          ]
        }}
        
        CRITICAL: The response MUST be a valid JSON object that can be directly parsed. Do not include any explanation or markdown formatting outside the JSON structure. Ensure ALL required fields are included with appropriate values.
        """
    
    def create_quiz_prompt(self, request, lesson_context: Dict) -> str:
        """Create a detailed prompt for quiz generation"""
        difficulty = request.difficulty_level.value if hasattr(request, 'difficulty_level') and request.difficulty_level else "intermediate"
        num_questions = request.num_questions if hasattr(request, 'num_questions') else 5
        include_explanations = request.include_explanations if hasattr(request, 'include_explanations') else True
        
        return f"""
        As an expert assessment designer with expertise in educational testing and evaluation,
        create a comprehensive quiz based on the following specifications:
        
        # LESSON CONTEXT
        LESSON TITLE: {lesson_context.get('lesson_title', 'N/A')}
        LESSON OBJECTIVE: {lesson_context.get('lesson_objective', 'N/A')}
        
        # QUIZ SPECIFICATIONS
        DIFFICULTY LEVEL: {difficulty}
        NUMBER OF QUESTIONS: {num_questions}
        INCLUDE EXPLANATIONS: {include_explanations}
        
        # INSTRUCTIONS
        Design a comprehensive assessment that effectively evaluates understanding of the lesson content.
        Create a quiz with the following elements:
        
        1. A brief quiz introduction that:
           - Explains the purpose of the assessment
           - Provides clear instructions for completion
           
        2. {num_questions} questions that:
           - Are directly aligned with the lesson objective
           - Test different cognitive levels (knowledge, comprehension, application, analysis)
           - Use a variety of question types (predominantly multiple choice for this format)
           - Increase in complexity throughout the quiz
           
        For each question provide:
        - A clear, unambiguous question prompt
        - 4 options (labeled A, B, C, D) with only one correct answer
        - The correct answer clearly indicated
        - A brief explanation of why the answer is correct
        - A difficulty rating (easy, medium, hard)
        
        Set an appropriate passing score based on the quiz difficulty.
        
        You MUST format the response as a valid JSON object with the following structure:
        {{
          "quiz_introduction": "A brief introduction to the quiz...",
          "questions": [
            {{
              "question": "First question text?",
              "options": ["A. First option", "B. Second option", "C. Third option", "D. Fourth option"],
              "correct_answer": "B. Second option",
              "explanation": "Explanation of why B is correct...",
              "difficulty": "medium"
            }},
            {{
              "question": "Second question text?",
              "options": ["A. First option", "B. Second option", "C. Third option", "D. Fourth option"],
              "correct_answer": "A. First option",
              "explanation": "Explanation of why A is correct...",
              "difficulty": "easy"
            }}
          ],
          "passing_score": 80,
          "difficulty_level": "{difficulty}"
        }}
        
        CRITICAL: The response MUST be a valid JSON object that can be directly parsed. Do not include any explanation or markdown formatting outside the JSON structure. Ensure ALL required fields are included with appropriate values.
        """
