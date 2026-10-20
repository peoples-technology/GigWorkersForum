import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CardToken(Base):
    __tablename__ = "card_tokens"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)  # Random opaque URL-safe token
    member_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("members.id"), index=True, nullable=False
    )
    membership_number: Mapped[str] = mapped_column(String(30), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revocation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
