from datetime import datetime, timedelta, timezone
import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db import get_db, set_tenant_context
from app.models import User

password_hasher = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)

def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "role": str(user.role),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

async def authenticate_user(session: AsyncSession, username: str, password: str) -> User | None:
    user = await session.scalar(select(User).where(User.username == username, User.is_active.is_(True)))
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)) -> User:
    error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id, tenant_id, role = payload.get("sub"), payload.get("tenant_id"), payload.get("role")
        if not user_id or not tenant_id:
            raise error
    except InvalidTokenError as exc:
        raise error from exc
    try:
        parsed_user_id = uuid.UUID(user_id)
    except ValueError as exc:
        raise error from exc
    user = await session.get(User, parsed_user_id)
    if not user or not user.is_active:
        raise error
    if str(user.tenant_id) != tenant_id or str(user.role) != role:
        raise error
    return user

async def tenant_session(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    await set_tenant_context(session, str(current_user.tenant_id))
    yield session

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    role = getattr(current_user.role, "value", current_user.role)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user
