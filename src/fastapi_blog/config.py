from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DATA_DIR = PACKAGE_DIR / "data"
MEDIA_DIR = PACKAGE_DIR / "media"
PROFILE_PICS_DIR = MEDIA_DIR / "profile_pics"
DEFAULT_PROFILE_IMAGE = "/media/profile_pics/default.jpg"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "FastAPI Blog"
    debug: bool = False
    post_page_size: int = 10
    max_upload_size_bytes: int = 5 * 1024 * 1024
    allowed_image_content_types: frozenset[str] = frozenset(
        {"image/jpeg", "image/png", "image/webp", "image/gif"}
    )

    @property
    def database_url(self) -> str:
        PROJECT_DATA_DIR.mkdir(parents=True, exist_ok=True)
        db_path = PROJECT_DATA_DIR / "blog.db"
        return f"sqlite:///{db_path}"

    @property
    def media_root(self) -> Path:
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        PROFILE_PICS_DIR.mkdir(parents=True, exist_ok=True)
        return MEDIA_DIR


settings = Settings()
