"""Replaceable LLM provider implementations.

Purpose:
    Provide a minimal generation interface for local and hosted model
    providers without coupling intelligence modules to vendor APIs.

Architecture notes:
    Providers return raw model text. They do not parse evidence, create
    database records, manage repositories, score outputs, or make domain
    decisions.

Future extension guidance:
    Keep new providers small and transport-focused. Structured output
    validation belongs in the caller that owns the output contract.
"""

from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Optional
from urllib import request


class LLMProvider(ABC):
    """Abstract text-generation provider."""

    provider_name = "abstract"

    def __init__(self, model_name):
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt, system_prompt=None):
        """Return raw model text for the supplied prompt."""


class QwenProvider(LLMProvider):
    """Local Qwen provider using Ollama."""

    provider_name = "qwen"

    def __init__(self, model_name="qwen3:8b"):  # Model name
        super().__init__(model_name=model_name)

    def generate(self, prompt, system_prompt=None):
        """Generate text through the local Ollama Python package."""
        try:
            from ollama import chat
        except ImportError as exc:
            raise RuntimeError("QwenProvider requires the ollama package") from exc

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})
        response = chat(model=self.model_name, messages=messages)
        message = getattr(response, "message", None)

        if message is not None:
            return getattr(message, "content", "")

        if isinstance(response, dict):
            return response.get("message", {}).get("content", "")

        return ""


class OpenAICompatibleProvider(LLMProvider):
    """Provider for OpenAI-compatible chat completion endpoints."""

    provider_name = "openai_compatible"

    def __init__(
        self,
        model_name,
        base_url,
        api_key=None,
        default_headers=None,
        timeout_seconds=60,
    ):
        super().__init__(model_name=model_name)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_headers = dict(default_headers or {})
        self.timeout_seconds = timeout_seconds

    def generate(self, prompt, system_prompt=None):
        """Generate text through a chat-completions-compatible HTTP endpoint."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            **self.default_headers,
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        http_request = request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers=headers,
            method="POST",
        )

        with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))

        return data["choices"][0]["message"]["content"]


class OpenRouterProvider(OpenAICompatibleProvider):
    """OpenRouter provider using its OpenAI-compatible endpoint."""

    provider_name = "openrouter"

    def __init__(
        self,
        model_name,
        api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers=None,
        timeout_seconds=60,
    ):
        headers = {
            "HTTP-Referer": "https://localhost/intelligence-platform",
            "X-Title": "Intelligence Platform",
        }
        headers.update(default_headers or {})
        super().__init__(
            model_name=model_name,
            base_url=base_url,
            api_key=api_key,
            default_headers=headers,
            timeout_seconds=timeout_seconds,
        )


def provider_from_environment(env: Optional[Dict[str, str]] = None):
    """Create a provider from environment settings, prioritizing local Qwen."""
    settings = env or os.environ
    provider = settings.get("LLM_PROVIDER", "qwen").casefold()

    if provider in {"qwen", "ollama", "local"}:
        return QwenProvider(
            model_name=settings.get("QWEN_MODEL", "qwen3:8b"),  # model name
        )

    if provider in {"openai", "openai_compatible", "compatible"}:
        return OpenAICompatibleProvider(
            model_name=settings.get("OPENAI_COMPATIBLE_MODEL", "qwen3:8b"),
            base_url=settings.get(
                "OPENAI_COMPATIBLE_BASE_URL",
                "http://localhost:11434/v1",
            ),
            api_key=settings.get("OPENAI_COMPATIBLE_API_KEY"),
        )

    if provider == "openrouter":
        return OpenRouterProvider(
            model_name=settings.get("OPENROUTER_MODEL", "qwen/qwen-2.5-7b-instruct"),
            api_key=settings.get("OPENROUTER_API_KEY", ""),
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")
