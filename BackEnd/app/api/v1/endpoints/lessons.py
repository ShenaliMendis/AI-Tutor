from fastapi import APIRouter, HTTPException
from app.models.lesson import LessonRequest, LessonResponse, QuizResponse
from app.services.ai_service import AIService

router = APIRouter(tags=["lessons"])
ai_service = AIService()

@router.post("/create-lesson-content", response_model=LessonResponse)
async def create_lesson_content(request: LessonRequest):
    # Prepare the prompt for lesson content creation
    prompt = f"""
    Create a detailed lesson based on the following information:
    
    LESSON TITLE: {request.lesson_title}
    LESSON OBJECTIVE: {request.lesson_objective}
    
    Generate comprehensive lesson content (800-1200 words) that thoroughly covers the topic. 
    The lesson content should include:
    - Clear explanations of concepts
    - Examples when appropriate
    - Practical applications when possible
    - Key takeaways or summary points
    """
    
    try:
        lesson_content = await ai_service.generate_content(prompt)
        
        # Validate response content
        if not lesson_content:
            raise HTTPException(status_code=500, detail="No response received from the model.")
        
        # Create a LessonResponse object
        lesson_response = LessonResponse(
            lesson_content=lesson_content
        )

        return lesson_response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lesson content: {str(e)}")

@router.post("/create-quiz", response_model=QuizResponse)
async def create_quiz(request: LessonRequest):
    # Prepare the prompt for quiz creation
    prompt = f"""
    Create a quiz based on the following lesson information:
    
    LESSON TITLE: {request.lesson_title}
    LESSON OBJECTIVE: {request.lesson_objective}
    
    Generate a quiz with 3-5 questions to test understanding. 
    For each quiz question provide:
    - A clear question
    - 4 possible answer options (A, B, C, D)
    - The correct answer
    - A brief explanation of why the answer is correct
    
    Format the response as a JSON object with the following structure:
    {{
      "quiz": [
        {{
          "question": "...",
          "options": ["A. option", "B. option", "C. option", "D. option"],
          "correct_answer": "B. option",
          "explanation": "..."
        }}
      ]
    }}
    """
    
    try:
        quiz_json = await ai_service.generate_structured_content(prompt)
        return QuizResponse(quiz=quiz_json.get("quiz", []))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")
