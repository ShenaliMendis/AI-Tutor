import json
from typing import Any, Dict
import google.generativeai as genai
from fastapi import HTTPException
from app.config import get_settings

class AIService:
    def __init__(self):
        settings = get_settings()
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Initialize the model
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.model_name)
    
    async def generate_content(self, prompt: str) -> str:
        """Generate content using the AI model"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")
    
    async def generate_structured_content(self, prompt: str) -> Dict[str, Any]:
        """Generate content and parse it as JSON"""
        try:
            response = await self.generate_content(prompt)
            
            # Remove markdown code block syntax if present
            if response.startswith("```json"):
                response = response.replace("```json", "", 1)
            if response.endswith("```"):
                response = response.replace("```", "", 1)
                
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Invalid JSON response: {str(e)}")
