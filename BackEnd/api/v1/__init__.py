from fastapi import APIRouter
from .routes import router as v1_router

router = APIRouter()
router.include_router(v1_router)
