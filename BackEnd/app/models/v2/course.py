from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

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
