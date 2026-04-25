"""Pydantic models for reusable agent definitions."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentMemoryConfig(BaseModel):
    """Memory preferences declared by an agent."""

    enabled: bool = True
    default_scope: str = "session"


class AgentContextPolicy(BaseModel):
    """Per-agent context policy overrides."""

    include_app_context: bool | None = None


class AgentDefinition(BaseModel):
    """A reusable agent definition loaded from an agent folder."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    version: str
    description: str
    personality_file: str = "personality.md"
    default_provider: str | None = None
    temperature: float | None = None
    memory: AgentMemoryConfig = Field(default_factory=AgentMemoryConfig)
    context_policy: AgentContextPolicy = Field(default_factory=AgentContextPolicy)
    metadata: dict[str, Any] = Field(default_factory=dict)

    source_dir: Path | None = None
    personality_path: Path | None = None
    personality: str | None = None

    @property
    def has_personality(self) -> bool:
        """Return whether personality markdown has been loaded."""

        return bool(self.personality)
