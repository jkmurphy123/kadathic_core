from agent_foundry.providers.base import ProviderChatRequest, ProviderMessage
from agent_foundry.providers.mock import MockProvider


def test_mock_provider_returns_deterministic_text() -> None:
    provider = MockProvider(provider_id="mock", model="mock-model")
    request = ProviderChatRequest(
        messages=[
            ProviderMessage(role="system", content="System instructions."),
            ProviderMessage(role="user", content="Hello"),
        ]
    )

    response = provider.chat(request)

    assert response.text == "[mock:mock] Hello"
    assert response.provider_id == "mock"
    assert response.model == "mock-model"
    assert response.metadata == {"message_count": 2}


def test_mock_provider_health_is_healthy() -> None:
    health = MockProvider(provider_id="mock", model="mock-model").health_check()

    assert health.provider_id == "mock"
    assert health.healthy is True
    assert health.model == "mock-model"
