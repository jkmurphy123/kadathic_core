"""Ollama provider adapter."""

from typing import Any

import httpx

from agent_foundry.providers.base import (
    ProviderChatRequest,
    ProviderChatResponse,
    ProviderHealth,
)


class OllamaProvider:
    """Provider adapter for Ollama's local `/api/chat` endpoint."""

    def __init__(
        self,
        *,
        provider_id: str,
        base_url: str = "http://localhost:11434",
        model: str,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.id = provider_id
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = client

    def chat(self, request: ProviderChatRequest) -> ProviderChatResponse:
        """Call Ollama `/api/chat` and return provider-neutral text."""

        model = request.model or self.model
        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            "stream": False,
        }
        if request.temperature is not None:
            payload["options"] = {"temperature": request.temperature}

        response = self._post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        text = data.get("message", {}).get("content")
        if not isinstance(text, str):
            text = ""

        return ProviderChatResponse(
            text=text,
            provider_id=self.id,
            model=model,
            usage=_usage_from_ollama_response(data),
            metadata={
                "done": data.get("done"),
                "total_duration": data.get("total_duration"),
            },
        )

    def health_check(self) -> ProviderHealth:
        """Return graceful health status for the Ollama server."""

        try:
            response = self._get("/api/tags")
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            return ProviderHealth(
                provider_id=self.id,
                healthy=False,
                message=f"Ollama unavailable at {self.base_url}: {exc}",
                model=self.model,
            )

        model_names = _model_names_from_tags(data)
        if self.model not in model_names:
            return ProviderHealth(
                provider_id=self.id,
                healthy=False,
                message=f"Ollama server is reachable, but model '{self.model}' is not installed.",
                model=self.model,
                metadata={"installed_models": sorted(model_names)},
            )

        return ProviderHealth(
            provider_id=self.id,
            healthy=True,
            message="Ollama server is reachable and the configured model is installed.",
            model=self.model,
            metadata={"installed_models": sorted(model_names)},
        )

    def _post(self, path: str, *, json: dict[str, Any]) -> httpx.Response:
        if self._client is not None:
            return self._client.post(f"{self.base_url}{path}", json=json)
        with httpx.Client(timeout=self.timeout) as client:
            return client.post(f"{self.base_url}{path}", json=json)

    def _get(self, path: str) -> httpx.Response:
        if self._client is not None:
            return self._client.get(f"{self.base_url}{path}")
        with httpx.Client(timeout=self.timeout) as client:
            return client.get(f"{self.base_url}{path}")


def _usage_from_ollama_response(data: dict[str, Any]) -> dict[str, Any]:
    usage_keys = [
        "prompt_eval_count",
        "prompt_eval_duration",
        "eval_count",
        "eval_duration",
    ]
    return {key: data[key] for key in usage_keys if key in data}


def _model_names_from_tags(data: dict[str, Any]) -> set[str]:
    models = data.get("models", [])
    if not isinstance(models, list):
        return set()

    names = set()
    for model in models:
        if not isinstance(model, dict):
            continue
        for key in ("name", "model"):
            value = model.get(key)
            if isinstance(value, str):
                names.add(value)
    return names
