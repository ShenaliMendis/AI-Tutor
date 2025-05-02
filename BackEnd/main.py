from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1.router import router as v1_router
# Future imports for v2 would go here
# from app.api.v2.router import router as v2_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="TuteAI Course Generator API",
        description="AI-powered course generation system",
        version="1.0.0"
    )
    
    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Modify with your frontend domains in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register API routers
    app.include_router(v1_router)
    # For future versions:
    # app.include_router(v2_router)
    
    @app.get("/")
    async def root():
        return {"message": "Welcome to TuteAI API. Go to /docs for documentation."}
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
