from fastapi import APIRouter, HTTPException, status
from app.models.v2.module import ModuleRequest, ModuleResponse, LessonInfo, ActivityInfo
from app.models.v2.course import ResourceItem
from app.services.ai_service_v2 import AIServiceV2
from app.utils.id_generator import generate_id
import json
import re
import logging

# Configure logging
logger = logging.getLogger("course_generation_api")

router = APIRouter(tags=["modules"])
ai_service = AIServiceV2()

# In-memory storage for module data
module_store = {}

# Reference to course store from courses.py
from app.api.v2.endpoints.courses import course_store

@router.post("/plan-module", response_model=ModuleResponse)
async def plan_module(request: ModuleRequest):
    # Get course information if available
    course_context = {}
    
    if request.course_id in course_store:
        course_context = course_store[request.course_id]
    else:
        # Use minimal context if course data is not available
        course_context = {
            "course_title": "Course",
            "course_description": "Course description not available",
            "target_audience_description": "Target audience not specified"
        }
    
    # Prepare the prompt for module planning
    prompt = ai_service.create_module_planning_prompt(request, course_context)
    
    try:
        # Generate module plan
        logger.info(f"Generating module plan for: {request.module_title}")
        module_data = await ai_service.generate_ai_content(prompt, temperature=0.7)
        
        # Clean and parse the response
        if "```" in module_data:
            json_match = re.search(r'```(?:json)?(.*?)```', module_data, re.DOTALL)
            if json_match:
                module_data = json_match.group(1).strip()
        
        # Parse the JSON with explicit error handling
        try:
            module_json = json.loads(module_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Raw response: {module_data}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse AI response. Please try again."
            )
        
        # Validate required fields in the response
        required_fields = ["module_introduction", "learning_path", "lessons"]
        for field in required_fields:
            if field not in module_json:
                logger.error(f"Missing required field in response: {field}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"AI response missing required field: {field}"
                )
        
        # Add IDs to lessons and activities
        module_id = generate_id("mod")
        lessons_with_ids = []
        
        # Validate and process lessons
        if not isinstance(module_json["lessons"], list) or len(module_json["lessons"]) == 0:
            logger.error("Lessons field is not a valid list or is empty")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI response contained invalid lessons data"
            )
        
        for i, lesson in enumerate(module_json["lessons"]):
            # Ensure lesson has required fields
            lesson_required_fields = ["lesson_title", "lesson_objective", "estimated_duration", "key_points"]
            for field in lesson_required_fields:
                if field not in lesson:
                    logger.error(f"Lesson {i} missing required field: {field}")
                    # Provide default values for missing fields
                    if field == "lesson_title":
                        lesson["lesson_title"] = f"Lesson {i+1}"
                    elif field == "lesson_objective":
                        lesson["lesson_objective"] = f"Learn key concepts in this lesson"
                    elif field == "estimated_duration":
                        lesson["estimated_duration"] = "30-60 minutes"
                    elif field == "key_points":
                        lesson["key_points"] = ["Key concept 1", "Key concept 2"]
            
            # Ensure key_points is a list
            if not isinstance(lesson["key_points"], list):
                logger.warning(f"Lesson {i}: key_points is not a list, converting")
                if isinstance(lesson["key_points"], str):
                    lesson["key_points"] = [lesson["key_points"]]
                else:
                    lesson["key_points"] = ["Key point 1", "Key point 2"]
            
            lesson_with_id = {
                "lesson_id": generate_id("les"),
                "lesson_title": lesson["lesson_title"],
                "lesson_objective": lesson["lesson_objective"],
                "estimated_duration": lesson["estimated_duration"],
                "key_points": lesson["key_points"]
            }
            lessons_with_ids.append(LessonInfo(**lesson_with_id))
        
        # Process activities if present
        activities_with_ids = []
        if "activities" in module_json and isinstance(module_json["activities"], list):
            for i, activity in enumerate(module_json["activities"]):
                # Ensure activity has required fields
                activity_required_fields = ["activity_title", "activity_type", "activity_description", "estimated_duration"]
                for field in activity_required_fields:
                    if field not in activity:
                        logger.error(f"Activity {i} missing required field: {field}")
                        # Provide default values for missing fields
                        if field == "activity_title":
                            activity["activity_title"] = f"Activity {i+1}"
                        elif field == "activity_type":
                            activity["activity_type"] = "exercise"
                        elif field == "activity_description":
                            activity["activity_description"] = "Complete the activity to reinforce your learning"
                        elif field == "estimated_duration":
                            activity["estimated_duration"] = "15-30 minutes"
                
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
        if "resources" in module_json and isinstance(module_json["resources"], list):
            try:
                resources = []
                for i, resource in enumerate(module_json["resources"]):
                    # Ensure resource has required fields
                    resource_required_fields = ["title", "description", "type"]
                    for field in resource_required_fields:
                        if field not in resource:
                            logger.warning(f"Resource {i} missing field: {field}")
                            if field == "title":
                                resource["title"] = f"Resource {i+1}"
                            elif field == "description":
                                resource["description"] = "Additional learning resource"
                            elif field == "type":
                                resource["type"] = "reference"
                    
                    resources.append(ResourceItem(**resource))
            except Exception as e:
                logger.warning(f"Error processing resources: {str(e)}")
                # Continue without resources if there's an error
        
        # Create the response object
        module_response = ModuleResponse(
            module_id=module_id,
            module_introduction=module_json["module_introduction"],
            learning_path=module_json["learning_path"],
            lessons=lessons_with_ids,
            activities=activities_with_ids if activities_with_ids else None,
            resources=resources
        )
        
        # Store module context in memory for lesson generation
        module_context_data = {
            "module_title": request.module_title,
            "module_summary": request.module_summary,
            "difficulty_level": request.difficulty_level.value if request.difficulty_level else None,
            "content_style": request.content_style.value if request.content_style else None
        }
        module_store[module_id] = module_context_data
        
        return module_response
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating module: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating module: {str(e)}"
        )
