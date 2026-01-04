from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from redis import Redis

from app.api.v1.router import api_router
from app.services.embeddings import get_sbert_model
from app.core.config import settings
from app.db.deps import get_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    logger.info(f"ATS-IA v{settings.APP_VERSION} starting in {settings.ENVIRONMENT} mode...")
    
    # Préchargement SBERT au démarrage (évite le "1er appel lent")
    try:
        get_sbert_model()
        logger.info("SBERT preloaded successfully.")
    except Exception as e:
        # Ne bloque pas le démarrage si SBERT échoue
        logger.warning(f"SBERT preload failed (will fallback to 0.0): {repr(e)}")
    
    yield
    
    # Shutdown
    logger.info("ATS-IA shutting down...")


app = FastAPI(
    title="ATS IA - API",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS - dynamically loaded from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.get("/ping")
def ping():
    """Simple ping endpoint for basic monitoring (no auth required)."""
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with dependency checks."""
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # Check database
    try:
                from sqlalchemy import text
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        from redis import Redis
        redis_client = Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)
        redis_client.ping()
        health_status["checks"]["redis"] = "ok"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = f"error: {str(e)}"
    
    # Check SBERT
    try:
        model = get_sbert_model()
        health_status["checks"]["sbert"] = "loaded" if model else "not_loaded"
    except Exception as e:
        health_status["checks"]["sbert"] = f"error: {str(e)}"
    
    # Return 503 if unhealthy
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    from fastapi import Response
    return Response(
        content=str(health_status),
        status_code=status_code,
        media_type="application/json"
    )
