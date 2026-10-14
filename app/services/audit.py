import hashlib
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AuditEvent, User

def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

async def write_audit(session: AsyncSession, actor: User, action: str, object_type: str, object_id: str | uuid.UUID, detail: dict | None = None) -> None:
    session.add(AuditEvent(
        tenant_id=actor.tenant_id,
        actor_id=actor.id,
        action=action,
        object_type=object_type,
        object_id=str(object_id),
        detail=detail or {},
    ))
