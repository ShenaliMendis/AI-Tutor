from pydantic import BaseModel
from typing import List

class LessonRequest(BaseModel):
    lesson_title: str
    lesson_objective: str

class LessonResponse(BaseModel):
    lesson_content: str

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

class QuizResponse(BaseModel):
    quiz: List[QuizQuestion]
