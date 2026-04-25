"""Inspectable context capsule for one agent turn."""

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from agent_foundry.context.app_context import AppContext
from agent_foundry.providers.base import ProviderMessage


class ContextCapsule(BaseModel):
    """A complete context packet assembled for one provider request."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    project_id: str
    agent_id: str
    session_id: str

    system_instructions: str
    agent_personality: str
    project_context: str | None = None
    memory_context: str | None = None
    session_summary: str | None = None
    recent_messages: list[ProviderMessage] = Field(default_factory=list)
    app_context: AppContext | None = None
    current_user_message: str

    rendered_messages: list[ProviderMessage]
    metadata: dict[str, Any] = Field(default_factory=dict)
