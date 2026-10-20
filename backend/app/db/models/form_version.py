from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class FormVersion(Base):
    __tablename__ = "form_versions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., 'v1.0'
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Ordered list of field specs:
    # [{key, type, labels: {ml, en}, required: bool, options: list, validation: dict, is_archived: bool}]
    fields: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
