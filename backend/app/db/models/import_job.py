import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ImportJob(Base):
    __tablename__ = "imports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    admin_id: Mapped[str] = mapped_column(String(100), nullable=False)
    admin_unit_id: Mapped[str] = mapped_column(String(50), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    # Status: 'queued', 'processing', 'completed', 'failed'
    status: Mapped[str] = mapped_column(String(30), default="queued", nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accepted_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ImportRow(Base):
    __tablename__ = "import_rows"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("imports.id"), index=True, nullable=False
    )
    row_index: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Status: 'accepted', 'rejected', 'skipped'
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    member_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    membership_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
