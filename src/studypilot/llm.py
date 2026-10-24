from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from studypilot.config import get_settings


def get_llm() -> BaseChatModel:
    """Erzeugt das in der Koknfig eingestellte Chat-Modell"""
    settings = get_settings()
    kwargs: dict = {"temperature": settings.llm_temperature}

    if settings.llm_provider == "openai":
        if settings.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY fehlt in der .env")
        kwargs["api_key"] = settings.openai_api_key.get_secret_value()
    elif settings.llm_provider == "anthoropic":
            if settings.anthropic_api_key is None:
                raise ValueError("ANTHROPIC_API_KEY fehlt in der .env")
            kwargs["api_key"] = settings.anthropic_api_key.get_secret_value()
    elif settings.llm_provider == "ollama":
            kwargs["base_url"] = settings.ollama_base_url

    return init_chat_model(settings.llm_model , model_provider=settings.llm_provider, **kwargs)