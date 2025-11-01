import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "test-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "test-bucket"
    S3_ENDPOINT_URL: str = "http://localhost:4566"

    PROJECT_NAME: str = "Project Management API"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "project_management"
    POSTGRES_PORT: str = "5432"

    class Config:
        env_file = ".env"


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

settings = Settings()
