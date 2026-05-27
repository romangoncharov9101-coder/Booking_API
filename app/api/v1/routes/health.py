from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=['health'])

@router.get('/health', summary='Liveness probe')
async def health() -> ORJSONResponse:
    return ORJSONResponse({'status': 'ok', 'version': settings.APP_VERSION})

@router.get('/health/ready', summary='Readiness probe - checks DB connectivity')
async def readiness(db: AsyncSession = Depends(get_db)) -> ORJSONResponse:
    try:
        await db.execute(text('SELECT 1'))
        db_status = 'ok'
    except Exception as e:
        db_status = f'error: {e}'

    ready = db_status == 'ok'
    return ORJSONResponse(
        status_code=200 if ready else 503,
        content={
            'status': 'ready' if ready else 'not_ready',
            'checks': {'database': db_status},
        }
    )