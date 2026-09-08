import os
from pathlib import Path
from typing import Any, List, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")


class Settings(BaseSettings):
    # Paths
    ROOT_DIR: Path = ROOT_DIR
    SRC_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = ROOT_DIR / "data"

    # Application
    APP_NAME: str = "Predicción Deportiva"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")

    # Database
    DB_USER: str = os.getenv("DB_USER", "prediccion_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "change_me")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "prediccion_deportiva")

    DATABASE_URL: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        elif self.DATABASE_URL.startswith("sqlite:///"):
            raw_path = self.DATABASE_URL[len("sqlite:///"):]
            if not Path(raw_path).is_absolute():
                cleaned = raw_path.lstrip("./")
                abs_db_path = (self.ROOT_DIR / cleaned).resolve()
                self.DATABASE_URL = f"sqlite:///{abs_db_path.as_posix()}"

        for attr in ["ML_MODELS_DIR", "ML_FEATURES_CACHE_DIR", "LOG_FILE"]:
            val = getattr(self, attr, None)
            if val and not Path(val).is_absolute():
                cleaned = val.lstrip("./")
                setattr(self, attr, str((self.ROOT_DIR / cleaned).resolve()))

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "5000"))

    # Scraping
    SCRAPER_USER_AGENT_ROTATE: bool = os.getenv("SCRAPER_USER_AGENT_ROTATE", "True").lower() == "true"
    SCRAPER_DELAY_MIN: float = float(os.getenv("SCRAPER_DELAY_MIN", "1.0"))
    SCRAPER_DELAY_MAX: float = float(os.getenv("SCRAPER_DELAY_MAX", "3.0"))
    SCRAPER_PROXY_ENABLED: bool = os.getenv("SCRAPER_PROXY_ENABLED", "False").lower() == "true"
    SCRAPER_PROXY_LIST: Optional[str] = os.getenv("SCRAPER_PROXY_LIST")

    # ML
    ML_MODELS_DIR: str = os.getenv("ML_MODELS_DIR", "./data/models")
    ML_FEATURES_CACHE_DIR: str = os.getenv("ML_FEATURES_CACHE_DIR", "./data/cache")
    ML_RANDOM_SEED: int = int(os.getenv("ML_RANDOM_SEED", "42"))
    ML_TRAIN_TEST_SPLIT: float = float(os.getenv("ML_TRAIN_TEST_SPLIT", "0.8"))
    ML_CV_FOLDS: int = int(os.getenv("ML_CV_FOLDS", "5"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./data/logs/app.log")

    # External APIs
    FOOTBALL_DATA_API_KEY: Optional[str] = os.getenv("FOOTBALL_DATA_API_KEY")
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

