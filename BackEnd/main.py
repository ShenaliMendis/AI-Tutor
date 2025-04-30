# File: main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Advanced Course Generation API",
    description="Enterprise-grade API for generating adaptive learning content using Google Generative AI",
    version="1.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Import API router with error handling
try:
    from api import router as api_router
    # Include API routes
    app.include_router(api_router)
except ImportError as e:
    print(f"Error importing API router: {e}")
    print("This might be due to an incompatibility with aioredis and Python 3.11.")
    print("Please run 'pip uninstall aioredis' and 'pip install redis' to fix.")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the AI Tutor API",
        "documentation": "/docs",
        "version": "1.0.0"
    }

# # Legacy API endpoints (for backward compatibility)
@app.post("/api/plan-course")
async def legacy_plan_course(request: Request):
    """Legacy endpoint that redirects to v1 API"""
    from api.v1.routes import CourseRequest  # Add import
    data = await request.json()
    try:
        course_request = CourseRequest(**data)  # Create Pydantic model
        from api.v1.routes import plan_course
        return await plan_course(course_request)  # Pass the model instance
    except ImportError:
        return JSONResponse(
            status_code=500,
            content={"detail": "API module import error. Please check server logs."}
        )

# Similarly update other legacy endpoints
@app.post("/api/plan-module")
async def legacy_plan_module(request: Request):
    """Legacy endpoint that redirects to v1 API"""
    from api.v1.routes import ModuleRequest  # Add import
    data = await request.json()
    try:
        module_request = ModuleRequest(**data)  # Create model instance
        from api.v1.routes import plan_module
        return await plan_module(module_request)
    except ImportError:
        return JSONResponse(
            status_code=500,
            content={"detail": "API module import error. Please check server logs."}
        )

@app.post("/api/create-lesson-content")
async def legacy_create_lesson_content(request: Request):
    """Legacy endpoint that redirects to v1 API"""
    from api.v1.routes import LessonRequest  # Add import
    data = await request.json()
    try:
        lesson_request = LessonRequest(**data)  # Create model instance
        from api.v1.routes import create_lesson_content
        return await create_lesson_content(lesson_request)
    except ImportError:
        return JSONResponse(
            status_code=500,
            content={"detail": "API module import error. Please check server logs."}
        )

@app.post("/api/create-quiz")
async def legacy_create_quiz(request: Request):
    """Legacy endpoint that redirects to v1 API"""
    from api.v1.routes import LessonRequest  # Add import
    data = await request.json()
    try:
        quiz_request = LessonRequest(**data)  # Create model instance
        from api.v1.routes import create_quiz
        return await create_quiz(quiz_request)
    except ImportError:
        return JSONResponse(
            status_code=500,
            content={"detail": "API module import error. Please check server logs."}
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"An error occurred: {str(exc)}"}
    )

# Run the application if executed directly
if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
