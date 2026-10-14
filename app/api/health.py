from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.ollama import ollama

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/live")
async def live():
    return {"status": "ok"}

@router.get("/ready")
async def ready(session: AsyncSession = Depends(get_db)):
    try:
        await session.execute(text("SELECT 1"))
        if not await ollama.health():
            raise RuntimeError("Ollama unavailable")
        return {"status": "ready", "database": "ok", "ollama": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
