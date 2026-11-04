import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


load_dotenv()

APP_VERSION = "2.2.0"


def _bool_env(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in {"true", "1", "yes", "on"}


class Settings:
    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
        self.DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")
        self.ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
        self.SESSION_SECRET = os.getenv("SESSION_SECRET", "")
        self.DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "deepseek-flash")
        self.TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
        self.ENABLE_WEB_SEARCH = _bool_env("ENABLE_WEB_SEARCH", True)
        self.ENABLE_SCHEDULER = _bool_env("ENABLE_SCHEDULER", True)
        self.ENABLE_DOCS = _bool_env("ENABLE_DOCS", False)
        self.SEARCH_MAX_RESULTS = int(os.getenv("SEARCH_MAX_RESULTS", "5"))
        data_dir = Path(os.getenv("DATA_DIR", "data"))
        self.DATA_DIR = (data_dir if data_dir.is_absolute() else project_root / data_dir).resolve()
        self.ALLOWED_ORIGINS = [v.strip() for v in os.getenv("ALLOWED_ORIGINS", "").split(",") if v.strip()]
        self.SESSION_MAX_AGE = int(os.getenv("SESSION_MAX_AGE", "28800"))
        self.MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "40000"))
        self.MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "4096"))

    def validate_security(self) -> None:
        problems = []
        weak = {"kindle-secret-token", "kindle-secret-token-123456", "changeme", "password"}
        if len(self.AUTH_TOKEN) < 32 or self.AUTH_TOKEN.lower() in weak:
            problems.append("AUTH_TOKEN must be a unique random value of at least 32 characters")
        if len(self.ADMIN_PASSWORD) < 12 or self.ADMIN_PASSWORD.lower() in weak:
            problems.append("ADMIN_PASSWORD must be at least 12 characters")
        if len(self.SESSION_SECRET) < 32 or self.SESSION_SECRET.lower() in weak:
            problems.append("SESSION_SECRET must be a unique random value of at least 32 characters")
        if problems:
            raise RuntimeError("Unsafe configuration: " + "; ".join(problems))


settings = Settings()
