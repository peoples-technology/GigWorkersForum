from litestar import Controller, get
from sqlalchemy import select

from app.db.models import Unit
from app.db.seeds import KERALA_DISTRICTS
from app.db.session import async_session_factory


class UnitsController(Controller):
    path = "/api/units"

    @get()
    async def get_units(self) -> list[dict]:
        try:
            async with async_session_factory() as session:
                stmt = select(Unit).where(Unit.level == "district").order_by(Unit.name)
                result = await session.execute(stmt)
                units = result.scalars().all()
                if units:
                    return [
                        {
                            "id": str(u.id),
                            "name": u.name,
                            "name_ml": u.name_ml,
                            "code": u.code,
                        }
                        for u in units
                    ]
        except Exception:
            pass
        
        # Return fallback districts list for immediate responsiveness
        return [
            {"id": d["code"], "name": d["name"], "name_ml": d["name_ml"], "code": d["code"]}
            for d in KERALA_DISTRICTS
        ]
