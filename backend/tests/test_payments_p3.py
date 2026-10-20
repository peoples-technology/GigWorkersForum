import uuid
from datetime import date

import pytest
from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.payment.allocator import calculate_allocations, generate_receipt_number
from app.core.payment.mock_adapter import MockPaymentAdapter
from app.core.payment.razorpay_adapter import RazorpayAdapter
from app.db.models import Payment
from app.db.session import Base
from app.main import app

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


def test_allocation_calculation_registration():
    """FR3.1: Sign-up ₹160 = ₹100 registration + 6 months at ₹10."""
    allocations, paid_up_to = calculate_allocations(
        amount_inr=160,
        is_initial_registration=True,
    )
    assert len(allocations) == 7  # 1 registration + 6 months
    assert allocations[0]["type"] == "registration_fee"
    assert allocations[0]["amount"] == 100
    assert all(a["amount"] == 10 for a in allocations[1:])
    assert paid_up_to > date.today()


def test_allocation_calculation_pay_ahead():
    """FR3.2: Pay ahead N months (e.g. 12 months = ₹120)."""
    current_paid = date(2027, 4, 30)
    allocations, new_paid_up_to = calculate_allocations(
        amount_inr=120,
        is_initial_registration=False,
        current_paid_up_to=current_paid,
    )
    assert len(allocations) == 12
    assert new_paid_up_to.year >= 2028


def test_receipt_number_generation():
    """FR3.8: Numbered digital receipt format."""
    rec = generate_receipt_number()
    assert rec.startswith(f"REC-{date.today().year}-")
    assert len(rec) >= 15


def test_payment_provider_signature_verification():
    """FR3.4: Payment provider webhook signature validation."""
    mock = MockPaymentAdapter(secret="citu_secret_key")
    payload = b'{"event": "payment.captured"}'

    # Deterministic valid signature check
    assert mock.verify_webhook_signature(payload, "valid_test_signature", "citu_secret_key") is True
    assert mock.verify_webhook_signature(payload, "invalid_signature", "citu_secret_key") is False

    rzp = RazorpayAdapter(key_secret="rzp_secret_123")
    import hashlib
    import hmac

    correct_sig = hmac.new(b"rzp_secret_123", payload, hashlib.sha256).hexdigest()
    assert rzp.verify_webhook_signature(payload, correct_sig, "rzp_secret_123") is True


@pytest.mark.asyncio
async def test_append_only_ledger_enforcement(test_session: AsyncSession):
    """FR3.5: No UPDATE or DELETE allowed on Payment table rows."""
    p = Payment(
        id=uuid.uuid4(),
        member_id=uuid.uuid4(),
        amount=160,
        payment_type="online",
        provider="mock",
        provider_payment_id="pay_test_immutable_1",
        allocations=[],
        paid_up_to=date(2027, 5, 31),
        receipt_number="REC-2026-99999",
        status="completed",
    )
    test_session.add(p)
    await test_session.commit()

    # Attempt to UPDATE -> must raise RuntimeError
    with pytest.raises(RuntimeError, match="Append-only ledger violation"):
        p.amount = 200
        await test_session.commit()

    await test_session.rollback()

    # Re-fetch or create fresh payment object to test delete
    p2 = Payment(
        id=uuid.uuid4(),
        member_id=uuid.uuid4(),
        amount=160,
        payment_type="online",
        provider="mock",
        provider_payment_id="pay_test_immutable_2",
        allocations=[],
        paid_up_to=date(2027, 5, 31),
        receipt_number="REC-2026-99998",
        status="completed",
    )
    test_session.add(p2)
    await test_session.commit()

    # Attempt to DELETE -> must raise RuntimeError
    with pytest.raises(RuntimeError, match="Append-only ledger violation"):
        await test_session.delete(p2)
        await test_session.commit()


@pytest.mark.asyncio
async def test_create_order_endpoint():
    """FR3.1, FR3.2: Order creation API."""
    async with AsyncTestClient(app=app) as client:
        res = await client.post(
            "/api/payments/create-order",
            json={"member_id": "mem_123", "months_ahead": 6, "is_initial_registration": True},
        )
        assert res.status_code == HTTP_200_OK
        data = res.json()
        assert data["success"] is True
        assert data["amount_inr"] == 160
        assert data["breakdown"]["registration_fee"] == 100
        assert data["breakdown"]["months"] == 6


@pytest.mark.asyncio
async def test_webhook_idempotency_endpoint():
    """FR3.6: Idempotent webhook handler keyed on provider_payment_id."""
    payload = {
        "provider": "mock",
        "provider_payment_id": "pay_mock_idempotent_123",
        "provider_order_id": "order_123",
        "amount_inr": 160,
        "member_id": str(uuid.uuid4()),
        "signature": "valid_test_signature",
        "is_initial_registration": True,
    }

    async with AsyncTestClient(app=app) as client:
        # First call -> success / activated
        res1 = await client.post("/api/payments/webhook", json=payload)
        assert res1.status_code == HTTP_200_OK
        assert res1.json()["success"] is True

        # Second call with same payment id -> idempotent
        res2 = await client.post("/api/payments/webhook", json=payload)
        assert res2.status_code == HTTP_200_OK
        assert res2.json()["success"] is True


@pytest.mark.asyncio
async def test_offline_payment_and_receipt():
    """FR3.7, FR3.8: Admin offline payment and receipt summary."""
    async with AsyncTestClient(app=app) as client:
        # 1. Offline payment entry
        offline_res = await client.post(
            "/api/payments/offline",
            json={
                "member_id": str(uuid.uuid4()),
                "amount_inr": 160,
                "payment_method": "cash",
                "reference": "PAPER-REC-1042",
                "is_initial_registration": True,
                "admin_id": "admin_tvm",
            },
        )
        assert offline_res.status_code == HTTP_200_OK
        receipt_no = offline_res.json()["receipt_number"]
        assert receipt_no.startswith("REC-")

        # 2. Receipt download
        rec_res = await client.get(f"/api/payments/receipt/{receipt_no}")
        assert rec_res.status_code == HTTP_200_OK
        rec_data = rec_res.json()
        assert rec_data["receipt_number"] == receipt_no
        assert "Kerala State Gig & Platform Workers Union" in rec_data["union"]["name"]
