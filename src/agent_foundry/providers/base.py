"""Provider-neutral request, response, and health models."""

from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field


class ProviderMessage(BaseModel):
    """A provider-neutral chat message."""

    role: Literal["system", "user", "assistant"]
    content: str


class ProviderChatRequest(BaseModel):
    """A provider-neutral chat request."""

    messages: list[ProviderMessage]
    model: str | None = None
    temperature: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderChatResponse(BaseModel):
    """A provider-neutral chat response."""

    text: str
    provider_id: str
    model: str | None = None
    usage: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderHealth(BaseModel):
    """Health check result for a provider."""

    provider_id: str
    healthy: bool
    message: str
    model: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderAdapter(Protocol):
    """Protocol implemented by provider adapters."""

    id: str

    def chat(self, request: ProviderChatRequest) -> ProviderChatResponse:
        """Return a chat response for a provider-neutral request."""

    def health_check(self) -> ProviderHealth:
        """Return provider health information."""
