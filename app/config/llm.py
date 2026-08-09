"""Shared LLM client. All agents pull their model from here so the whole
app can be pointed at a different Ollama model (or endpoint) in one place.
"""
from langchain_ollama import ChatOllama

from app.config.settings import settings


def get_llm(temperature: float = 0.2) -> ChatOllama:
    """Return a configured Ollama chat model."""
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=temperature,
    )
