"""Application configuration settings using pydantic-settings."""

from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global firewall system configuration."""

    # Metadata
    APP_NAME: str = "AI Prompt Injection and Jailbreak Detection Firewall"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./firewall.db"

    # Security & Auth
    JWT_SECRET_KEY: str = "change-this-super-secret-key-in-production-minimum-32-chars-entropy"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Detection & Risk Scoring
    DEFAULT_ML_THRESHOLD: float = 0.70
    RULE_BLOCK_THRESHOLD: float = 0.80
    REVIEW_THRESHOLD: float = 0.50
    SECURE_MODE: bool = False

    # LLM Gateway
    LLM_PROVIDER: str = "mock"  # mock | ollama | openai | rest
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    REST_LLM_URL: str = ""
    REST_LLM_METHOD: str = "POST"
    LLM_TIMEOUT_SECONDS: float = 15.0

    # Constraints & Audit Controls
    MAX_PROMPT_LENGTH: int = 10000
    MAX_BATCH_SIZE: int = 50
    LOG_FULL_PROMPTS: bool = False

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:80"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def APP_DIR(self) -> Path:
        return Path(__file__).resolve().parent

    @property
    def DATA_DIR(self) -> Path:
        data_path = self.BASE_DIR / "data"
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path

    @property
    def ARTIFACTS_DIR(self) -> Path:
        artifacts_path = self.APP_DIR / "ml" / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)
        return artifacts_path

    @property
    def REPORTS_DIR(self) -> Path:
        reports_path = self.BASE_DIR / "reports"
        reports_path.mkdir(parents=True, exist_ok=True)
        return reports_path


settings = Settings()
