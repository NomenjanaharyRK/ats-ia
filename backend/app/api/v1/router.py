from fastapi import APIRouter
from app.api.v1.offers import router as offers_router
from app.api.v1.auth import router as auth_router
from app.api.v1.applications import router as applications_router



api_router = APIRouter(prefix="/api/v1")
api_router.include_router(offers_router)
api_router.include_router(auth_router)
api_router.include_router(applications_router)
