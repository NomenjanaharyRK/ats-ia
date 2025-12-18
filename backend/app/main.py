from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(title="ATS IA - API")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router)
