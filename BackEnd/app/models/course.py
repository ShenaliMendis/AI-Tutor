from pydantic import BaseModel, Field
from typing import List, Optional

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
