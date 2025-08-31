from pydantic_settings import BaseSettings
from typing import Optional, List
import json

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    GEMINI_API_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int
    JWT_REFRESH_EXPIRE_MINUTES: int
    REDIS_URL: str
    DEBUG: bool
    ENVIRONMENT: str
    CORS_ORIGINS: List[str]
    
    @classmethod
    def load_from_env(cls):
        return cls()
    
    @property
    def database_url(self):
        return self.DATABASE_URL
    
    @property
    def openai_api_key(self):
        return self.OPENAI_API_KEY
    
    @property
    def anthropic_api_key(self):
        return self.ANTHROPIC_API_KEY
    
    @property
    def gemini_api_key(self):
        return self.GEMINI_API_KEY
    
    @property
    def jwt_secret(self):
        return self.JWT_SECRET
    
    @property
    def jwt_algorithm(self):
        return self.JWT_ALGORITHM
    
    @property
    def jwt_expire_minutes(self):
        return self.JWT_EXPIRE_MINUTES
    
    @property
    def redis_url(self):
        return self.REDIS_URL
    
    @property
    def debug(self):
        return self.DEBUG
    
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        try:
            return json.loads(self.CORS_ORIGINS)
        except json.JSONDecodeError:
            return ["https://localhost:3000", "https://localhost:5173"]
    
    @property
    def environment(self):
        return self.ENVIRONMENT

    class Config:
        env_file = ".env"

settings = Settings()