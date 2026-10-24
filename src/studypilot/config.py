from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Zentrale Konfiguration, gelesen aus Umgebungsvariablen bzw. der .env-Datei."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: Literal["openai", "anthropic", "ollama"] = "ollama"
    llm_model: str
    llm_temperature: float = 0.2

    open_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    ollama_base_url: str = "http://localhost:11434"

@lru_cache
def get_settings() -> Settings:
    return Settings()