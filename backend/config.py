from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

         
    groq_api_key: str
    groq_model_large: str = "llama-3.3-70b-versatile"
    groq_model_small: str = "llama-3.1-8b-instant"

        
    database_url: str

             
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    app_env: str = "development"
    secret_key: str = "dev-secret"

                                                                                  
    pubmed_api_key: str | None = None
    rxnav_base_url: str = "https://rxnav.nlm.nih.gov/REST"
    openfda_base_url: str = "https://api.fda.gov"

              
    backend_base_url: str = "http://localhost:8000"

@lru_cache
def get_settings() -> Settings:
    return Settings()
