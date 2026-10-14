from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import require_admin, tenant_session
from app.models import AuditEvent, User
from app.schemas import AuditOut

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("", response_model=list[AuditOut])
async def list_audit_events(admin: User = Depends(require_admin), session: AsyncSession = Depends(tenant_session)):
    stmt = select(AuditEvent).where(AuditEvent.tenant_id == admin.tenant_id).order_by(AuditEvent.created_at.desc()).limit(250)
    return list((await session.scalars(stmt)).all())
