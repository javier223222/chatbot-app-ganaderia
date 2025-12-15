# src/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.infrastructure.database import get_db
from src.services.agent_service import AgentService


router = APIRouter(prefix="/chat", tags=["Chat Agent"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    tool_used: str = None
    tool_result: str = None


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal del chatbot.
    Permite hacer consultas en lenguaje natural sobre el ganado.
    
    Ejemplos de consultas:
    - "¿Cuándo le toca vacuna a la vaca 504?"
    - "Muéstrame todo mi ganado"
    - "¿Qué vacas están preñadas?"
    - "¿Tengo recordatorios pendientes?"
    """
    agent = AgentService(db)
    result = await agent.chat(request.message)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return ChatResponse(
        response=result["response"],
        tool_used=result.get("tool_used"),
        tool_result=result.get("tool_result")
    )


@router.get("/health")
def health_check():
    """Verifica que el servicio de chat esté funcionando"""
    return {"status": "ok", "service": "chat-agent"}
