"""Public runtime request and response models."""

from typing import Any

from pydantic import BaseModel, Field

from agent_foundry.context.app_context import AppContext


class ChatRequest(BaseModel):
    """Request model for a single runtime chat turn."""

    agent_id: str
    project_id: str
    session_id: str
    user_id: str
    user_message: str
    app_context: AppContext | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Response model returned by `AgentRuntime.chat`."""

    text: str
    agent_id: str
    session_id: str
    provider_id: str
    model: str | None = None
    context_capsule_id: str | None = None
    usage: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
