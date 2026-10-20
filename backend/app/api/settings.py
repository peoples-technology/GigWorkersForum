from litestar import Controller, get
from sqlalchemy import select

from app.db.models import Setting
from app.db.session import async_session_factory


class SettingsController(Controller):
    path = "/api/settings"

    @get()
    async def get_public_settings(self) -> dict:
        try:
            async with async_session_factory() as session:
                stmt = select(Setting)
                result = await session.execute(stmt)
                settings_list = result.scalars().all()
                return {s.key: s.value for s in settings_list}
        except Exception:
            # Fallback safe defaults if database is not yet migrated
            return {
                "module_autopay": {"enabled": False},
                "module_automated_lapse": {"enabled": False, "grace_period_months": 6},
                "module_grievance_filing": {"enabled": False, "contacts_display": True},
                "fee_structure": {
                    "registration_fee": 100,
                    "monthly_fee": 10,
                    "default_advance_months": 6,
                    "total_initial_amount": 160,
                },
            }
