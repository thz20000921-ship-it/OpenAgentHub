import os
import secrets
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Config
    PROJECT_NAME: str = "OpenAgentHub"
    VERSION: str = "3.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database Config
    DB_PATH: str = os.environ.get("OPENAGENT_DB_PATH", os.path.join(os.getcwd(), "openagent.db"))
    
    # Security
    API_KEY: str = os.environ.get("OPENAGENT_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

if not settings.API_KEY:
    settings.API_KEY = secrets.token_urlsafe(32)
    print(f"\n🔑 Generated API Key (set OPENAGENT_API_KEY env var to override):\n   {settings.API_KEY}\n")
