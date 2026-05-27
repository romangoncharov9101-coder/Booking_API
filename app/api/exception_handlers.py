from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from app.core.exceptions import AppError
from app.core.logging import get_logger

logger = get_logger(__name__)

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> ORJSONResponse:
        logger.warning(
            'app_error',
            error_code=exc.error_code,
            message=exc.message,
            path=request.url.path,
        )
        return ORJSONResponse(
            status_code=exc.status_code,
            content={'error': {'code': exc.error_code, 'message': exc.message, 'details': exc.details}},
        )
    
    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> ORJSONResponse:
        logger.exception('unhandled_error', path=request.url.path, exc_info=exc)
        return ORJSONResponse(
            status_code=500,
            content={'error': {'code': 'INTERNAL_EROR', 'message': 'An unexpected error occured.', 'details': {}}},
        )