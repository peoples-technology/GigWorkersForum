import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.unit import Unit


async def allocate_membership_number(
    db: AsyncSession,
    unit_id: uuid.UUID | str,
) -> str:
    """
    Allocate the next sequential membership number for a district unit (FR4.1).
    Uses row-level locking (SELECT ... FOR UPDATE) to ensure concurrency safety.
    Format: {DISTCODE}{6-digit-counter}, e.g. 'KLEKM000042'.
    """
    if isinstance(unit_id, str):
        try:
            unit_id = uuid.UUID(unit_id)
        except ValueError:
            # Fallback if code or string passed
            stmt = select(Unit).where(Unit.code == unit_id).with_for_update()
            res = await db.execute(stmt)
            unit = res.scalar_one_or_none()
            if not unit:
                raise ValueError(f"District unit '{unit_id}' not found.")
            unit.current_counter += 1
            return f"{unit.code}{unit.current_counter:06d}"

    stmt = select(Unit).where(Unit.id == unit_id).with_for_update()
    res = await db.execute(stmt)
    unit = res.scalar_one_or_none()

    if not unit:
        raise ValueError(f"District unit with ID '{unit_id}' not found.")

    unit.current_counter += 1
    membership_number = f"{unit.code}{unit.current_counter:06d}"
    return membership_number
