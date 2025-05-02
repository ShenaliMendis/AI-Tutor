import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "TuteAI"
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    model_name: str = "gemini-2.0-flash-exp"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
