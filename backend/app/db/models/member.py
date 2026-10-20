import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Member(Base):
    __tablename__ = "members"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    working_unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("units.id"), nullable=False)
    membership_number: Mapped[str | None] = mapped_column(
        String(30), unique=True, index=True, nullable=True
    )
    # Status: 'pending', 'active', 'suspended'
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="ml", nullable=False)
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    photo_pending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # DPDP Compliance: Masked ID storage only
    id_doc_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    id_last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    encrypted_id_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Form version & answers JSONB
    form_version_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    answers: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Consent
    consented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
