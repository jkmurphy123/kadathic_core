"""Deterministic provider used by tests and local development."""

from agent_foundry.providers.base import (
    ProviderChatRequest,
    ProviderChatResponse,
    ProviderHealth,
)


class MockProvider:
    """Provider adapter that requires no network or external service."""

    def __init__(self, provider_id: str = "mock", model: str | None = "mock-model") -> None:
        self.id = provider_id
        self.model = model

    def chat(self, request: ProviderChatRequest) -> ProviderChatResponse:
        """Return a deterministic response based on the latest user message."""

        user_messages = [message.content for message in request.messages if message.role == "user"]
        latest_user_message = user_messages[-1] if user_messages else ""
        model = request.model or self.model
        return ProviderChatResponse(
            text=f"[mock:{self.id}] {latest_user_message}",
            provider_id=self.id,
            model=model,
            metadata={"message_count": len(request.messages)},
        )

    def health_check(self) -> ProviderHealth:
        """Return a healthy status for the mock provider."""

        return ProviderHealth(
            provider_id=self.id,
            healthy=True,
            message="Mock provider is available.",
            model=self.model,
        )
