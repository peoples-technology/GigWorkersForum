import uuid
from datetime import UTC, date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String, event
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class FeeSchedule(Base):
    __tablename__ = "fee_schedules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    fee_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'registration', 'monthly_subscription'
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # in INR
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    member_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("members.id"), index=True, nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # in INR
    payment_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # 'online', 'offline_cash', 'offline_upi', 'reversal'
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'razorpay', 'cashfree', 'offline_manual'
    provider_payment_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    provider_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    allocations: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    paid_up_to: Mapped[date] = mapped_column(Date, nullable=False)
    receipt_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default="completed", nullable=False
    )  # 'completed', 'reversed'
    logged_by_admin_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    offline_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


# Append-only ledger enforcement at the SQLAlchemy ORM layer (FR3.5)
@event.listens_for(Payment, "before_update")
def receive_before_update(mapper, connection, target):
    raise RuntimeError(
        "Append-only ledger violation: Payments cannot be UPDATEd. Use reversal entries."
    )


@event.listens_for(Payment, "before_delete")
def receive_before_delete(mapper, connection, target):
    raise RuntimeError("Append-only ledger violation: Payments cannot be DELETEd.")
