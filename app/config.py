from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Airtable
    AIRTABLE_API_KEY: str
    AIRTABLE_BASE_ID: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./integration.db"
    
    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Webhook
    WEBHOOK_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()