import asyncio
from sqlalchemy import select
from app.core.config import settings
from app.core.security import hash_password
from app.db import SessionLocal
from app.models import Tenant, User

async def bootstrap() -> None:
    async with SessionLocal() as session:
        tenant = await session.scalar(select(Tenant).where(Tenant.slug == settings.bootstrap_tenant_slug))
        if not tenant:
            tenant = Tenant(slug=settings.bootstrap_tenant_slug, name="Demo Regulated Tenant")
            session.add(tenant)
            await session.flush()
        admin = await session.scalar(select(User).where(User.username == settings.bootstrap_admin_username))
        if not admin:
            session.add(User(
                tenant_id=tenant.id,
                username=settings.bootstrap_admin_username,
                password_hash=hash_password(settings.bootstrap_admin_password),
                role="admin",
            ))
        await session.commit()

if __name__ == "__main__":
    asyncio.run(bootstrap())
