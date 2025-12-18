from fastapi import APIRouter
from app.api.v1.offers import router as offers_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(offers_router)
