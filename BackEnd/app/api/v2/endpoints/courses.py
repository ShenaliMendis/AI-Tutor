from fastapi import APIRouter, HTTPException, status, Query
from app.models.v2.course import CourseRequest, CourseResponse, ResourceItem, ModuleInfo
from app.services.ai_service_v2 import AIServiceV2
from app.utils.id_generator import generate_id
from datetime import datetime
import json
import re
import logging

# Configure logging
logger = logging.getLogger("course_generation_api")

router = APIRouter(tags=["courses"])
ai_service = AIServiceV2()

# In-memory storage for course data
course_store = {}

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
async def plan_course(request: CourseRequest):
    # Prepare the prompt for course planning
    prompt = ai_service.create_course_planning_prompt(request)
    
    try:
        # Generate course plan
        logger.info(f"Generating course plan for: {request.title}")
        course_data = await ai_service.generate_ai_content(prompt, temperature=0.7)
        
        # Clean and parse the response
        if "```" in course_data:
            # Extract JSON from code blocks if present
            json_match = re.search(r'```(?:json)?(.*?)```', course_data, re.DOTALL)
            if json_match:
                course_data = json_match.group(1).strip()
        
        # Parse the JSON with explicit error handling
        try:
            course_json = json.loads(course_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Raw response: {course_data}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse AI response. Please try again."
            )
        
        # Validate required fields are present
        required_fields = ["course_title", "course_description", "course_introduction", 
                          "learning_outcomes", "prerequisites", "target_audience_description", 
                          "estimated_total_duration", "modules"]
        
        for field in required_fields:
            if field not in course_json:
                logger.error(f"Missing required field in response: {field}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"AI response missing required field: {field}"
                )
        
        # Check that modules have required fields
        modules_with_ids = []
        for i, module in enumerate(course_json["modules"]):
            # Ensure module has required fields
            module_required_fields = ["module_title", "module_summary", "estimated_duration", "key_concepts"]
            for field in module_required_fields:
                if field not in module:
                    logger.error(f"Module {i} missing required field: {field}")
                    # Add default values for missing fields
                    if field == "module_title":
                        module["module_title"] = f"Module {i+1}"
                    elif field == "module_summary":
                        module["module_summary"] = "Module details not provided."
                    elif field == "estimated_duration":
                        module["estimated_duration"] = "1-2 hours"
                    elif field == "key_concepts":
                        module["key_concepts"] = ["Concept 1", "Concept 2"]
            
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
            try:
                recommended_resources = [ResourceItem(**resource) for resource in course_json["recommended_resources"]]
            except Exception as e:
                logger.warning(f"Error parsing recommended resources: {str(e)}")
                # Continue without resources if there's an error
        
        # Create the response object
        course_id = generate_id("course")
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
        
        # Store course data in memory
        course_context_data = {
            "course_title": course_json["course_title"],
            "course_description": course_json["course_description"],
            "target_audience_description": course_json["target_audience_description"]
        }
        course_store[course_id] = course_context_data
        
        return course_response
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating course: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error generating course: {str(e)}"
        )

@router.get("/export-course/{course_id}", status_code=status.HTTP_200_OK)
async def export_course(
    course_id: str,
    format: str = Query("md", description="Export format: md, html, pdf")
):
    """
    Export an entire course in various formats
    """
    try:
        # Check if course exists
        if course_id not in course_store:
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
