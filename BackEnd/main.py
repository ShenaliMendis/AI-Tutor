from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.api.v1.router import router as v1_router
from app.api.v2.router import router as v2_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="TuteAI Course Generator API",
        description="AI-powered course generation system",
        version="2.0.0"
    )
    
    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Modify with your frontend domains in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Version check endpoint
    @app.get("/api/versions")
    async def api_versions():
        return {
            "versions": ["v1", "v2"],
            "current": "v2",
            "status": {
                "v1": "stable",
                "v2": "beta"
            }
        }
    
    # Register API routers
    app.include_router(v1_router)
    app.include_router(v2_router)
    
    # Mount static files
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
