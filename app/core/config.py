from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    APP_NAME: str = "Sportly"
    DEBUG: bool = False

    base_storage_path: Path = Path("static")
    avatar_path: Path = base_storage_path / "avatars"
    gym_path: Path = base_storage_path / "gyms"
    max_file_size: int = 5 * 1024 * 1024  # 5 MB
    allowed_extensions: list = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()