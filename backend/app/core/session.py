import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.session import SessionRecord


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


async def create_session(
    session: AsyncSession,
    user_id: str,
    role: str,
    unit_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    duration_hours: int = 24,
) -> tuple[str, SessionRecord]:
    """Create a new server-side session in Postgres."""
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)
    expires_at = datetime.now(UTC) + timedelta(hours=duration_hours)

    record = SessionRecord(
        id=token_hash,
        user_id=user_id,
        role=role,
        unit_id=unit_id,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
    )
    session.add(record)
    await session.flush()
    return raw_token, record


async def get_session(
    session: AsyncSession,
    raw_token: str,
) -> SessionRecord | None:
    """Retrieve an active session from Postgres."""
    if not raw_token:
        return None

    token_hash = _hash_token(raw_token)
    now = datetime.now(UTC)

    stmt = select(SessionRecord).where(
        SessionRecord.id == token_hash,
        SessionRecord.expires_at > now,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def revoke_session(
    session: AsyncSession,
    raw_token: str,
) -> bool:
    """Revoke a session."""
    if not raw_token:
        return False

    token_hash = _hash_token(raw_token)
    stmt = delete(SessionRecord).where(SessionRecord.id == token_hash)
    result = await session.execute(stmt)
    return result.rowcount > 0
