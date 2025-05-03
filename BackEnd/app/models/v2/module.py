from pydantic import BaseModel
from typing import List, Optional
from app.models.v2.course import DifficultyLevel, ContentStyle, ResourceItem

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
