from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.services.embeddings import get_sbert_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Préchargement SBERT au démarrage (évite le "1er appel lent")
    try:
        get_sbert_model()
        print("SBERT preloaded successfully.")
    except Exception as e:
        # Ne bloque pas le démarrage si SBERT échoue
        print("SBERT preload failed (will fallback to 0.0):", repr(e))

    yield
    # (optionnel) code de shutdown ici


app = FastAPI(title="ATS IA - API", lifespan=lifespan)

# CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
