from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str
    env: str

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # Authentication settings
    secret_key: str = "your-secret-key-change-in-production-min-32-chars"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:"
            f"{self.db_password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
    