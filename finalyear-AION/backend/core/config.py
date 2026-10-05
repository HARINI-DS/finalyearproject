from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_DIR = ROOT_DIR / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    app_name: str = "AION"
    host: str = os.getenv("AION_HOST", "127.0.0.1")
    port: int = int(os.getenv("AION_PORT", "8000"))
    frontend_url: str = os.getenv("AION_FRONTEND_URL", "http://127.0.0.1:5173")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    db_url: str = os.getenv("AION_DB_URL", "sqlite:///../database/aion.db")


settings = Settings()
