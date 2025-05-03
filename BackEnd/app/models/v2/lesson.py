from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.v2.course import DifficultyLevel, ContentStyle, ResourceItem

class LessonRequest(BaseModel):
    module_id: str
    lesson_title: str
    lesson_objective: str
    difficulty_level: Optional[DifficultyLevel] = None
    content_style: Optional[ContentStyle] = None
    focus_areas: Optional[List[str]] = None

class ContentSection(BaseModel):
    heading: str
    content: str
    importance: int = 1

class LessonResponse(BaseModel):
    lesson_id: str
    lesson_title: str
    introduction: str
    sections: List[ContentSection]
    summary: str
    reflection_questions: List[str]
    next_steps: str
    resources: Optional[List[ResourceItem]] = None

class QuizRequest(BaseModel):
    lesson_id: str
    difficulty_level: Optional[DifficultyLevel] = DifficultyLevel.INTERMEDIATE
    num_questions: Optional[int] = Field(5, ge=3, le=10)
    include_explanations: Optional[bool] = True

class QuizQuestion(BaseModel):
    question_id: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    difficulty: str

class QuizResponse(BaseModel):
    quiz_id: str
    lesson_id: str
    quiz_introduction: str
    questions: List[QuizQuestion]
    passing_score: int
    difficulty_level: str
