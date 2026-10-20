from litestar import Controller, get
from litestar.response import Response
from sqlalchemy import text

from app.config import get_settings
from app.db.session import async_session_factory

settings = get_settings()


class HealthController(Controller):
    path = "/health"

    @get()
    async def check_health(self) -> dict:
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "env": settings.APP_ENV,
        }

    @get("/ready")
    async def check_readiness(self) -> Response[dict]:
        try:
            async with async_session_factory() as session:
                await session.execute(text("SELECT 1"))
            return Response(
                content={"status": "ready", "database": "connected"},
                status_code=200,
            )
        except Exception as e:
            return Response(
                content={"status": "degraded", "database": str(e)},
                status_code=503,
            )
