from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DEEPSEEK_API_KEY: str
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/opsmind"
    DATABASE_URL_ASYNC: str = "postgresql://postgres:postgres@localhost:5432/opsmind"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"


settings = Settings()
