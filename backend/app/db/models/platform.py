import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., 'swiggy', 'zomato'
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sector: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'food_delivery', 'cab_mobility', 'quick_commerce'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PlatformEntry(Base):
    __tablename__ = "platform_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    member_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("members.id"), index=True, nullable=False
    )
    platform_id: Mapped[str] = mapped_column(ForeignKey("platforms.id"), nullable=False)
    sector: Mapped[str] = mapped_column(String(50), nullable=False)
    zone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
