import json

import httpx
import pytest

from agent_foundry.core.errors import ConfigurationError
from agent_foundry.providers.base import ProviderChatRequest, ProviderMessage
from agent_foundry.providers.deepseek import DeepSeekProvider


def test_deepseek_provider_formats_request_and_parses_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret-key")
    captured_payload = {}
    captured_authorization = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_payload, captured_authorization
        captured_payload = json.loads(request.content.decode("utf-8"))
        captured_authorization = request.headers.get("authorization")
        return httpx.Response(
            200,
            request=request,
            json={
                "id": "completion-id",
                "model": "deepseek-chat",
                "choices": [
                    {"message": {"role": "assistant", "content": "Provider response"}}
                ],
                "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
            },
        )

    provider = DeepSeekProvider(
        provider_id="deepseek",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    response = provider.chat(
        ProviderChatRequest(
            messages=[ProviderMessage(role="user", content="Hello")],
            temperature=0.1,
        )
    )

    assert captured_payload == {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.1,
    }
    assert captured_authorization == "Bearer secret-key"
    assert response.text == "Provider response"
    assert response.provider_id == "deepseek"
    assert response.model == "deepseek-chat"
    assert response.usage == {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5}
    assert response.metadata == {"id": "completion-id"}


def test_deepseek_provider_uses_defaults_when_not_configured() -> None:
    provider = DeepSeekProvider(provider_id="deepseek")

    assert provider.base_url == "https://api.deepseek.com"
    assert provider.api_key_env == "DEEPSEEK_API_KEY"
    assert provider.model == "deepseek-chat"


def test_deepseek_provider_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    provider = DeepSeekProvider(provider_id="deepseek")

    with pytest.raises(ConfigurationError, match="Set environment variable DEEPSEEK_API_KEY"):
        provider.chat(ProviderChatRequest(messages=[ProviderMessage(role="user", content="Hello")]))


def test_deepseek_health_check_reports_missing_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    provider = DeepSeekProvider(provider_id="deepseek")

    health = provider.health_check()

    assert health.healthy is False
    assert "Set environment variable DEEPSEEK_API_KEY" in health.message


def test_deepseek_health_check_reports_configured_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret-key")
    provider = DeepSeekProvider(provider_id="deepseek")

    health = provider.health_check()

    assert health.healthy is True
    assert health.message == "API key is configured. Use providers smoke to verify generation."
