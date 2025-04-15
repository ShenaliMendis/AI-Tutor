# File: main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import uuid
from google.generativeai import GenerativeModel
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI(title="Course Generation API", description="API for generating courses using Google Generative AI")

# Data models
class LearningObjective(BaseModel):
    objective: str

class CourseRequest(BaseModel):
    title: str
    description: str
    target_audience: str
    time_available: str
    learning_objectives: Optional[List[str]] = None
    preferred_format: Optional[str] = "text-heavy"

class ModuleInfo(BaseModel):
    module_id: str
    module_title: str
    module_summary: str

class CourseResponse(BaseModel):
    course_title: str
    course_description: str
    course_introduction: str
    modules: List[ModuleInfo]

class ModuleRequest(BaseModel):
    module_title: str
    module_summary: str

class LessonInfo(BaseModel):
    lesson_id: str
    lesson_title: str
    lesson_objective: str

class ModuleResponse(BaseModel):
    module_introduction: str
    lessons: List[LessonInfo]

class LessonRequest(BaseModel):
    lesson_title: str
    lesson_objective: str

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

class LessonResponse(BaseModel):
    lesson_content: str
    quiz: List[QuizQuestion]

# Helper function to generate unique IDs
def generate_id(prefix=""):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

# Initialize the model
model = GenerativeModel("gemini-1.5-pro")

@app.post("/api/plan-course", response_model=CourseResponse)
async def plan_course(request: CourseRequest):
    # Prepare the prompt for course planning
    objectives_text = "\n".join([f"- {obj}" for obj in request.learning_objectives]) if request.learning_objectives else "No specific objectives provided."
    
    prompt = f"""
    Create a comprehensive course plan based on the following information:
    
    TITLE: {request.title}
    DESCRIPTION: {request.description}
    TARGET AUDIENCE: {request.target_audience}
    TIME AVAILABLE: {request.time_available}
    PREFERRED FORMAT: {request.preferred_format}
    
    LEARNING OBJECTIVES:
    {objectives_text}
    
    Generate a structured course with the following:
    1. A refined course title
    2. An engaging course description (3-5 sentences)
    3. A compelling course introduction (1-2 paragraphs)
    4. 3-6 logical modules that cover the subject matter comprehensively
    
    For each module provide:
    - A clear title
    - A brief summary (2-3 sentences)
    
    Format the response as a JSON object with the following structure:
    {{
      "course_title": "...",
      "course_description": "...",
      "course_introduction": "...",
      "modules": [
        {{
          "module_title": "...",
          "module_summary": "..."
        }}
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        course_data = response.text
        
        # Remove markdown code block syntax if present
        if course_data.startswith("```json"):
            course_data = course_data.replace("```json", "", 1)
        if course_data.endswith("```"):
            course_data = course_data.replace("```", "", 1)
            
        import json
        course_json = json.loads(course_data.strip())
        
        # Add module_id to each module
        modules_with_ids = []
        for i, module in enumerate(course_json["modules"]):
            module_with_id = {
                "module_id": generate_id("mod"),
                "module_title": module["module_title"],
                "module_summary": module["module_summary"]
            }
            modules_with_ids.append(module_with_id)
        
        course_response = {
            "course_title": course_json["course_title"],
            "course_description": course_json["course_description"],
            "course_introduction": course_json["course_introduction"],
            "modules": modules_with_ids
        }
        
        return course_response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating course: {str(e)}")

@app.post("/api/plan-module", response_model=ModuleResponse)
async def plan_module(request: ModuleRequest):
    # Prepare the prompt for module planning
    prompt = f"""
    Create a detailed module plan based on the following information:
    
    MODULE TITLE: {request.module_title}
    MODULE SUMMARY: {request.module_summary}
    
    Generate:
    1. A compelling module introduction (1 paragraph)
    2. 3-5 logical lessons that cover the module content comprehensively
    
    For each lesson provide:
    - A clear title
    - A specific learning objective
    
    Format the response as a JSON object with the following structure:
    {{
      "module_introduction": "...",
      "lessons": [
        {{
          "lesson_title": "...",
          "lesson_objective": "..."
        }}
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        module_data = response.text
        
        # Remove markdown code block syntax if present
        if module_data.startswith("```json"):
            module_data = module_data.replace("```json", "", 1)
        if module_data.endswith("```"):
            module_data = module_data.replace("```", "", 1)
            
        import json
        module_json = json.loads(module_data.strip())
        
        # Add lesson_id to each lesson
        lessons_with_ids = []
        for i, lesson in enumerate(module_json["lessons"]):
            lesson_with_id = {
                "lesson_id": generate_id("les"),
                "lesson_title": lesson["lesson_title"],
                "lesson_objective": lesson["lesson_objective"]
            }
            lessons_with_ids.append(lesson_with_id)
        
        module_response = {
            "module_introduction": module_json["module_introduction"],
            "lessons": lessons_with_ids
        }
        
        return module_response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating module: {str(e)}")

@app.post("/api/create-lesson", response_model=LessonResponse)
async def create_lesson(request: LessonRequest):
    # Prepare the prompt for lesson creation
    prompt = f"""
    Create a detailed lesson and quiz based on the following information:
    
    LESSON TITLE: {request.lesson_title}
    LESSON OBJECTIVE: {request.lesson_objective}
    
    Generate:
    1. Comprehensive lesson content (800-1200 words) that thoroughly covers the topic
    2. A quiz with 3-5 questions to test understanding
    
    The lesson content should include:
    - Clear explanations of concepts
    - Examples when appropriate
    - Practical applications when possible
    - Key takeaways or summary points
    
    For each quiz question provide:
    - A clear question
    - 4 possible answer options (A, B, C, D)
    - The correct answer
    - A brief explanation of why the answer is correct
    
    Format the response as a JSON object with the following structure:
    {{
      "lesson_content": "...",
      "quiz": [
        {{
          "question": "...",
          "options": ["A. option", "B. option", "C. option", "D. option"],
          "correct_answer": "B. option",
          "explanation": "..."
        }}
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        lesson_data = response.text
        
        # Remove markdown code block syntax if present
        if lesson_data.startswith("```json"):
            lesson_data = lesson_data.replace("```json", "", 1)
        if lesson_data.endswith("```"):
            lesson_data = lesson_data.replace("```", "", 1)
            
        import json
        lesson_json = json.loads(lesson_data.strip())
        
        return lesson_json
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lesson: {str(e)}")

# Run the FastAPI app with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
