from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.audit import AuditLog


async def log_audit(
    session: AsyncSession,
    actor_id: str | None,
    actor_role: str,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """Write an append-only audit log entry."""
    entry = AuditLog(
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
    )
    session.add(entry)
    await session.flush()
    return entry
