from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.exception_handlers import register_exception_handlers
from app.api.v1.routes.health import router as health_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.session import engine

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    logger.info(
        'startup',
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        env=settings.ENVIRONMENT,
    )
    yield
    logger.info('shutdown')
    await engine.dispose()

def create_app() -> FastAPI:
    app = FastAPI(
        titla=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url='/docs' if not settings.is_production else None,
        redoc_url='/redoc' if not settings.is_production else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    register_exception_handlers(app)
    app.include_router(health_router)
    return app

app = create_app()