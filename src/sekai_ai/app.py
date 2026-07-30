from fastapi import FastAPI

from sekai_ai import __version__
from sekai_ai.api.routes import router
from sekai_ai.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(
        title="SekAI AI",
        version=__version__,
        docs_url="/docs" if resolved_settings.app_env != "prod" else None,
        redoc_url=None,
    )
    app.state.settings = resolved_settings
    app.include_router(router)
    return app
