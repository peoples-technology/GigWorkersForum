import uuid

import pytest
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from litestar.testing import AsyncTestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.audit import log_audit
from app.core.rate_limit import RateLimiter
from app.core.security import (
    generate_recovery_codes,
    generate_totp_secret,
    get_totp_code,
    hash_password,
    verify_password,
    verify_totp_code,
)
from app.core.session import create_session, get_session, revoke_session
from app.db.models import AuditLog
from app.db.session import Base
from app.main import app

# In-memory SQLite async engine for comprehensive DB tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_session():
    test_engine = create_async_engine(TEST_DB_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    await test_engine.dispose()


def test_argon2id_password_hashing():
    """FR8.1: Argon2id password hashing and verification."""
    raw_pwd = "SolidarityComrade@2026"
    hashed = hash_password(raw_pwd)

    assert hashed.startswith("$argon2id$")
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_totp_generation_and_verification():
    """FR7.9: TOTP 2FA secret generation and time-step verification."""
    secret = generate_totp_secret()
    assert len(secret) >= 20

    code = get_totp_code(secret)
    assert len(code) == 6
    assert code.isdigit()
    assert verify_totp_code(secret, code) is True
    assert verify_totp_code(secret, "000000") is False

    recovery_codes = generate_recovery_codes(8)
    assert len(recovery_codes) == 8
    assert all(len(c) == 8 for c in recovery_codes)


def test_rate_limiter_cooldown_and_window():
    """FR1.3 & NFR3.5: Rate limit OTP requests and cooldown per phone/IP."""
    test_limiter = RateLimiter()
    phone = "+919847099999"
    ip = "192.168.1.100"

    # First request: OK
    ok, err = test_limiter.check_otp_rate_limit(phone, ip, cooldown_seconds=45)
    assert ok is True
    assert err is None

    # Immediate second request: blocked by cooldown
    ok2, err2 = test_limiter.check_otp_rate_limit(phone, ip, cooldown_seconds=45)
    assert ok2 is False
    assert "Please wait" in (err2 or "")


@pytest.mark.asyncio
async def test_server_side_session_postgres(test_session: AsyncSession):
    """FR8.2: Server-side session creation, retrieval and revocation."""
    user_id = "+919847012345"
    raw_token, record = await create_session(
        session=test_session,
        user_id=user_id,
        role="member",
        ip_address="127.0.0.1",
        user_agent="Playwright Test",
    )
    await test_session.commit()

    assert raw_token is not None
    assert record.user_id == user_id

    # Retrieve session
    fetched = await get_session(test_session, raw_token)
    assert fetched is not None
    assert fetched.user_id == user_id
    assert fetched.role == "member"

    # Revoke session
    revoked = await revoke_session(test_session, raw_token)
    assert revoked is True
    await test_session.commit()

    after_revoke = await get_session(test_session, raw_token)
    assert after_revoke is None


@pytest.mark.asyncio
async def test_append_only_audit_log(test_session: AsyncSession):
    """FR7.8: Append-only audit log writing and query."""
    entry = await log_audit(
        session=test_session,
        actor_id="admin_ekm",
        actor_role="district_admin",
        action="member_exported",
        resource_type="members",
        resource_id=None,
        details={"format": "csv", "count": 140},
        ip_address="10.0.0.1",
    )
    await test_session.commit()

    stmt = select(AuditLog).where(AuditLog.id == entry.id)
    res = await test_session.execute(stmt)
    found = res.scalar_one()
    assert found.actor_id == "admin_ekm"
    assert found.action == "member_exported"
    assert found.details["count"] == 140


@pytest.mark.asyncio
async def test_admin_login_and_2fa_challenge():
    """FR7.9: Admin authentication flow with mandatory TOTP 2FA."""
    admin_id = uuid.uuid4()

    # Pre-populate challenge token
    from app.api.auth import _ADMIN_CHALLENGES

    async with AsyncTestClient(app=app) as client:
        # 1. Invalid login credentials
        bad_login = await client.post(
            "/api/auth/admin/login",
            json={"username": "state_gs", "password": "WrongPassword"},
        )
        assert bad_login.status_code == HTTP_401_UNAUTHORIZED

        # 2. Challenge token verification directly
        challenge_token = f"chal_{admin_id}_12345"
        _ADMIN_CHALLENGES[challenge_token] = str(admin_id)

        # 3. Invalid 2FA code
        bad_2fa = await client.post(
            "/api/auth/admin/2fa",
            json={"challenge_token": challenge_token, "totp_code": "000000"},
        )
        # Re-assert status or challenge
        assert bad_2fa.status_code in [HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED]
