from fastapi import APIRouter, HTTPException
from app.models.course import CourseRequest, CourseResponse, ModuleInfo
from app.services.ai_service import AIService
from app.utils.id_generator import generate_id

router = APIRouter(tags=["courses"])
ai_service = AIService()

@router.post("/plan-course", response_model=CourseResponse)
async def plan_course(request: CourseRequest):
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
        course_json = await ai_service.generate_structured_content(prompt)
        
        # Add module_id to each module
        modules_with_ids = []
        for module in course_json["modules"]:
            module_with_id = ModuleInfo(
                module_id=generate_id("mod"),
                module_title=module["module_title"],
                module_summary=module["module_summary"]
            )
            modules_with_ids.append(module_with_id)
        
        course_response = CourseResponse(
            course_title=course_json["course_title"],
            course_description=course_json["course_description"],
            course_introduction=course_json["course_introduction"],
            modules=modules_with_ids
        )
        
        return course_response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating course: {str(e)}")
