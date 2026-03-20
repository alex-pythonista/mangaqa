from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/mangaqa"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    HF_API_URL: str = "https://router.huggingface.co/hf-inference/models"
    HF_API_TOKEN: str = ""
    OPENROUTER_MODEL: str = "deepseek/deepseek-v3.2-20251201"
    OPENROUTER_RATE_LIMIT: int = 20
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    CORS_ORIGINS: str = "http://localhost:5173"
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env"}


settings = Settings()
