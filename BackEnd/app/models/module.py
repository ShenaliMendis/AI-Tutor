from pydantic import BaseModel
from typing import List

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
