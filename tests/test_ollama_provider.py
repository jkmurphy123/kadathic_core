import json

import httpx

from agent_foundry.providers.base import ProviderChatRequest, ProviderMessage
from agent_foundry.providers.ollama import OllamaProvider


def test_ollama_provider_formats_chat_request_and_parses_response() -> None:
    captured_payload = {}

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_payload
        captured_payload = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            request=request,
            json={
                "message": {"role": "assistant", "content": "Ollama response"},
                "done": True,
                "prompt_eval_count": 12,
                "eval_count": 4,
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OllamaProvider(
        provider_id="ollama_local",
        base_url="http://ollama.test",
        model="qwen",
        client=client,
    )

    response = provider.chat(
        ProviderChatRequest(
            messages=[
                ProviderMessage(role="system", content="System"),
                ProviderMessage(role="user", content="Hello"),
            ],
            temperature=0.2,
        )
    )

    assert captured_payload == {
        "model": "qwen",
        "messages": [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "Hello"},
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }
    assert response.text == "Ollama response"
    assert response.provider_id == "ollama_local"
    assert response.model == "qwen"
    assert response.usage["prompt_eval_count"] == 12
    assert response.usage["eval_count"] == 4


def test_ollama_health_check_healthy() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            request=request,
            json={"models": [{"name": "qwen", "model": "qwen"}]},
        )

    provider = OllamaProvider(
        provider_id="ollama_local",
        base_url="http://ollama.test",
        model="qwen",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    health = provider.health_check()

    assert health.provider_id == "ollama_local"
    assert health.healthy is True
    assert health.message == "Ollama server is reachable and the configured model is installed."
    assert health.model == "qwen"


def test_ollama_health_check_reports_missing_model() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, request=request, json={"models": [{"name": "llama3.1"}]})

    provider = OllamaProvider(
        provider_id="ollama_local",
        base_url="http://ollama.test",
        model="qwen",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    health = provider.health_check()

    assert health.provider_id == "ollama_local"
    assert health.healthy is False
    assert "model 'qwen' is not installed" in health.message


def test_ollama_health_check_reports_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    provider = OllamaProvider(
        provider_id="ollama_local",
        base_url="http://ollama.test",
        model="qwen",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    health = provider.health_check()

    assert health.provider_id == "ollama_local"
    assert health.healthy is False
    assert "Ollama unavailable" in health.message
