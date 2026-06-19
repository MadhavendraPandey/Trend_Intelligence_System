"""LLM provider abstractions for the Intelligence Platform.

Purpose:
    Expose replaceable model providers behind one small interface. Local Qwen
    via Ollama is the first priority, followed by OpenAI-compatible endpoints
    and OpenRouter.

Architecture notes:
    Core LLM providers do not know about trend, friction, evidence extraction,
    reports, repositories, or database storage. Modules depend on this layer
    when they need model text generation.

Future extension guidance:
    Add new providers by implementing `LLMProvider.generate`. Keep provider
    selection isolated here so module code does not depend on vendor-specific
    APIs.
"""

from core.llm.providers import (
    LLMProvider,
    OpenAICompatibleProvider,
    OpenRouterProvider,
    QwenProvider,
    provider_from_environment,
)

__all__ = [
    "LLMProvider",
    "OpenAICompatibleProvider",
    "OpenRouterProvider",
    "QwenProvider",
    "provider_from_environment",
]
