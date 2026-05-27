from functools import lru_cache
from typing import Literal
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    APP_NAME: str = 'Booking API'
    APP_VERSION: str = '0.1.0'
    ENVIRONMENT: Literal['local', 'test', 'staging', 'production'] = 'local'
    DEBUG: bool = False
    API_V1_PREFIX: str = '/api/v1'

    DATABASE_URL: str = ''
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_ECHO: bool = False

    JWT_SECRET_KEY: str = ''
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    REDIS_URL: str = ''

    SMTP_HOST: str = 'mailhog'
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str = ''
    SMTP_PASSWORD: str = ''
    SMTP_USE_TLS: bool = False
    EMAIL_FROM: str = 'no-reply@booking-api.local'
    EMAIL_FROM_NAME: str = 'Booking API'

    NEAR_FUTURE_HOURS: int = 48
    BOOKING_MAX_DAYS_AHEAD: int = 60
    BOOKING_MIN_NOTICE_MINUTES: int = 30

    RATE_LIMIT_LOGIN_PER_MINUTE: int = 10
    RATE_LIMIT_REGISTER_PER_MINUTE: int = 5

    CELERY_BROKER_URL: str = ''
    CELERY_RESULT_BACKEND: str = ''

    CORS_ORIGINS: list[str] = []

    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def assemble_db_user(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith('postgresql://'):
            return v.replace('postgresql://', 'postgresql+asyncpg://', 1)
        if isinstance(v, str) and v.startswith('postgresql+psycopg2://'):
            return v.replace('postgresql+psycopg2://', 'postgresql+asyncpg://', 1)
        return v
    
    @model_validator(mode='after')
    def validate_production_settings(self) -> 'Settings':
        if self.ENVIRONMENT == 'production':
            if self.JWT_SECRET_KEY in ('change-me', 'secret', ''):
                raise ValueError('JWT_SECRET_KEY must be set in production')
            if self.DEBUG:
                raise ValueError('DEBUG must be false in production')
        return self
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == 'production'
    
    @property
    def is_test(self) -> bool:
        return self.ENVIRONMENT == 'test'
    
@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()