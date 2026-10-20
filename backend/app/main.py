from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin, YamlRenderPlugin

from app.api.auth import AuthController
from app.api.cards import CardsController, VerifyController
from app.api.health import HealthController
from app.api.payments import PaymentsController
from app.api.registration import RegistrationController
from app.api.settings import SettingsController
from app.api.units import UnitsController
from app.config import get_settings

settings = get_settings()

cors_config = CORSConfig(
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)

openapi_config = OpenAPIConfig(
    title="CITU Kerala Gig Workers Union Platform API",
    version="1.0.0",
    description="Backend API for Kerala State Gig & Platform Workers Union (CITU / CPI(M))",
    render_plugins=[SwaggerRenderPlugin(), YamlRenderPlugin()],
)

app = Litestar(
    route_handlers=[
        HealthController,
        SettingsController,
        UnitsController,
        AuthController,
        RegistrationController,
        PaymentsController,
        CardsController,
        VerifyController,
    ],
    cors_config=cors_config,
    openapi_config=openapi_config,
    debug=settings.DEBUG,
)
