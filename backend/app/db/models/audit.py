import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    actor_role: Mapped[str] = mapped_column(String(50), nullable=False)
    # Roles: 'system', 'member', 'district_admin', 'state_admin'
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    # Actions: 'member_registered', 'payment_received', 'id_viewed', 'export_performed'
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
