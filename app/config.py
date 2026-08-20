import os
from typing import Optional

class Settings:
    def __init__(self):
        self.DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
        self.DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.AUTH_TOKEN: str = os.getenv("AUTH_TOKEN", "kindle-secret-token")
        self.DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "deepseek-chat")
        self.TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY", None)
        self.ENABLE_WEB_SEARCH: bool = os.getenv("ENABLE_WEB_SEARCH", "true").lower() in ("true", "1", "yes")
        self.SEARCH_MAX_RESULTS: int = int(os.getenv("SEARCH_MAX_RESULTS", "5"))

settings = Settings()
