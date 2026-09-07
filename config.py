from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # По умолчанию используем SQLite, но можно легко поменять на PostgreSQL
    database_url: str = "sqlite:///./conference.db"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
