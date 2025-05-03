from fastapi import APIRouter
from app.api.v2.endpoints import courses, modules, lessons, health

# Create the v2 router
router = APIRouter(prefix="/api/v2", tags=["v2"])

# Include all endpoint routers
router.include_router(courses.router)
router.include_router(modules.router)
router.include_router(lessons.router)
router.include_router(health.router)
