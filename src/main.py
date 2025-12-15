# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.infrastructure.database import engine, Base
from src.api.routes import chat

from src.models import Cattle, HealthEvent, HeatEventModel, Reminder

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API de gestión ganadera con asistente IA integrado",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(chat.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "API Ganadera lista",
        "chat_endpoint": f"{settings.API_V1_STR}/chat",
        "docs": "/docs"
    }