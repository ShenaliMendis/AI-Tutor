from fastapi import APIRouter, status
from datetime import datetime
import os
import json

router = APIRouter(tags=["health"])

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")

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

@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(feedback: dict):
    """
    Store user feedback for content and use it to improve future generations
    """
    try:
        feedback_id = f"feedback_{int(datetime.now().timestamp())}_{hash(str(feedback))}"
        
        # In a real implementation, store this in a database
        
        return {"status": "success", "feedback_id": feedback_id}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/generate-learning-path", status_code=status.HTTP_201_CREATED)
async def generate_learning_path(request: dict):
    """
    Generate a personalized learning path based on user goals and current knowledge
    """
    try:
        # This would be fully implemented in a production system
        path_id = f"path_{int(datetime.now().timestamp())}"
        
        return {
            "status": "success", 
            "path_id": path_id,
            "message": "Learning path generation started. Results will be available shortly."
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/debug", status_code=status.HTTP_200_OK)
async def debug_ai(request: dict):
    """
    Debug endpoint for testing AI responses
    """
    from app.services.ai_service_v2 import AIServiceV2
    
    try:
        ai_service = AIServiceV2()
        prompt = request.get("prompt", "Create a JSON response with the following structure: {\"test\": \"This is a test\"}")
        
        # Generate content
        content = await ai_service.generate_ai_content(prompt, temperature=0.2)
        
        # Try to parse as JSON
        json_data = None
        try:
            if "```" in content:
                import re
                json_match = re.search(r'```(?:json)?(.*?)```', content, re.DOTALL)
                if json_match:
                    content_cleaned = json_match.group(1).strip()
                    json_data = json.loads(content_cleaned)
            else:
                json_data = json.loads(content)
        except:
            pass
        
        return {
            "status": "success",
            "raw_content": content,
            "json_parsed": json_data is not None,
            "json_data": json_data
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
