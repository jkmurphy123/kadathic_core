"""DeepSeek chat completions provider adapter."""

import os
from typing import Any

import httpx

from agent_foundry.core.errors import ConfigurationError
from agent_foundry.providers._chat_completion import _text_from_chat_completion
from agent_foundry.providers.base import (
    ProviderChatRequest,
    ProviderChatResponse,
    ProviderHealth,
)


class DeepSeekProvider:
    """Provider adapter for the DeepSeek API (OpenAI-compatible).

    Sensible defaults mean a minimal config only needs ``type: deepseek``.
    """

    DEFAULT_BASE_URL = "https://api.deepseek.com"
    DEFAULT_API_KEY_ENV = "DEEPSEEK_API_KEY"
    DEFAULT_MODEL = "deepseek-chat"

    def __init__(
        self,
        *,
        provider_id: str,
        base_url: str | None = None,
        api_key_env: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.id = provider_id
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.api_key_env = api_key_env or self.DEFAULT_API_KEY_ENV
        self.model = model or self.DEFAULT_MODEL
        self.timeout = timeout
        self._client = client

    def chat(self, request: ProviderChatRequest) -> ProviderChatResponse:
        """Call the DeepSeek `/v1/chat/completions` endpoint."""

        model = request.model or self.model
        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
        }
        if request.temperature is not None:
            payload["temperature"] = request.temperature

        response = self._post("/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        text = _text_from_chat_completion(data)

        return ProviderChatResponse(
            text=text,
            provider_id=self.id,
            model=data.get("model") if isinstance(data.get("model"), str) else model,
            usage=data.get("usage") if isinstance(data.get("usage"), dict) else {},
            metadata={"id": data.get("id")},
        )

    def health_check(self) -> ProviderHealth:
        """Return whether the provider is minimally configured."""

        try:
            self._api_key()
        except ConfigurationError as exc:
            return ProviderHealth(
                provider_id=self.id,
                healthy=False,
                message=str(exc),
                model=self.model,
            )

        return ProviderHealth(
            provider_id=self.id,
            healthy=True,
            message="API key is configured. Use providers smoke to verify generation.",
            model=self.model,
        )

    def _post(self, path: str, *, json: dict[str, Any]) -> httpx.Response:
        headers = {"Authorization": f"Bearer {self._api_key()}"}
        if self._client is not None:
            return self._client.post(f"{self.base_url}{path}", json=json, headers=headers)
        with httpx.Client(timeout=self.timeout) as client:
            return client.post(f"{self.base_url}{path}", json=json, headers=headers)

    def _api_key(self) -> str:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise ConfigurationError(
                f"Missing API key for provider '{self.id}'. "
                f"Set environment variable {self.api_key_env}."
            )
        return api_key
