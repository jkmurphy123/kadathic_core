import json

import httpx
import pytest

from agent_foundry.core.errors import ConfigurationError
from agent_foundry.providers.base import ProviderChatRequest, ProviderMessage
from agent_foundry.providers.openai_compatible import OpenAICompatibleProvider


def test_openai_compatible_provider_formats_request_and_parses_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TEST_API_KEY", "secret-key")
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
                "model": "test-model",
                "choices": [
                    {"message": {"role": "assistant", "content": "Provider response"}}
                ],
                "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
            },
        )

    provider = OpenAICompatibleProvider(
        provider_id="compatible",
        base_url="https://provider.test",
        api_key_env="TEST_API_KEY",
        model="test-model",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    response = provider.chat(
        ProviderChatRequest(
            messages=[ProviderMessage(role="user", content="Hello")],
            temperature=0.1,
        )
    )

    assert captured_payload == {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.1,
    }
    assert captured_authorization == "Bearer secret-key"
    assert response.text == "Provider response"
    assert response.provider_id == "compatible"
    assert response.model == "test-model"
    assert response.usage == {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5}
    assert response.metadata == {"id": "completion-id"}


def test_openai_compatible_provider_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TEST_API_KEY", raising=False)
    provider = OpenAICompatibleProvider(
        provider_id="compatible",
        base_url="https://provider.test",
        api_key_env="TEST_API_KEY",
        model="test-model",
    )

    with pytest.raises(ConfigurationError, match="Set environment variable TEST_API_KEY"):
        provider.chat(ProviderChatRequest(messages=[ProviderMessage(role="user", content="Hello")]))


def test_openai_compatible_health_check_reports_missing_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TEST_API_KEY", raising=False)
    provider = OpenAICompatibleProvider(
        provider_id="compatible",
        base_url="https://provider.test",
        api_key_env="TEST_API_KEY",
        model="test-model",
    )

    health = provider.health_check()

    assert health.healthy is False
    assert "Set environment variable TEST_API_KEY" in health.message


def test_openai_compatible_health_check_reports_configured_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TEST_API_KEY", "secret-key")
    provider = OpenAICompatibleProvider(
        provider_id="compatible",
        base_url="https://provider.test",
        api_key_env="TEST_API_KEY",
        model="test-model",
    )

    health = provider.health_check()

    assert health.healthy is True
    assert health.message == "API key is configured. Use providers smoke to verify generation."
