import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    AUTH_TOKEN: str = os.getenv("AUTH_TOKEN", "kindle-secret-token")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "deepseek-chat")
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY", None)
    ENABLE_WEB_SEARCH: bool = os.getenv("ENABLE_WEB_SEARCH", "true").lower() in ("true", "1", "yes")
    SEARCH_MAX_RESULTS: int = int(os.getenv("SEARCH_MAX_RESULTS", "5"))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
