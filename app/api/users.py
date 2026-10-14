from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, require_admin
from app.db import get_db
from app.models import User
from app.schemas import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOut, status_code=201)
async def create_user(payload: UserCreate, admin: User = Depends(require_admin), session: AsyncSession = Depends(get_db)):
    existing = await session.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(tenant_id=admin.tenant_id, username=payload.username, password_hash=hash_password(payload.password), role=payload.role)
    session.add(user)
    await session.commit()
    return user
