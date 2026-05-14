"""Pydantic models for project configuration."""

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectMetadata(BaseModel):
    """Basic project identity."""

    id: str
    name: str | None = None


class ProviderConfig(BaseModel):
    """Configuration for one provider adapter."""

    model_config = ConfigDict(extra="allow")

    type: Literal["mock", "ollama", "openai_compatible", "deepseek"]
    model: str | None = None
    base_url: str | None = None
    api_key_env: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StorageConfig(BaseModel):
    """Local storage configuration placeholder for later milestones."""

    path: str = ".agentfoundry/agent_foundry.sqlite"


class ContextPolicyConfig(BaseModel):
    """Project-level context policy placeholder for later milestones."""

    include_app_context: bool = True
    max_recent_messages: int = 12
    app_context_position: str = "before_user_message"


class ProjectConfig(BaseModel):
    """Top-level `agentfoundry.yaml` configuration."""

    project: ProjectMetadata
    default_provider: str = "mock"
    providers: dict[str, ProviderConfig] = Field(default_factory=dict)
    agent_libraries: list[str] = Field(default_factory=list)
    enabled_agents: list[str] = Field(default_factory=list)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    context_policy: ContextPolicyConfig = Field(default_factory=ContextPolicyConfig)

    source_path: Path | None = None

    @property
    def source_dir(self) -> Path:
        """Return the directory containing this config file."""

        if self.source_path is None:
            return Path.cwd()
        return self.source_path.parent

    def resolved_agent_libraries(self) -> list[Path]:
        """Return agent library paths resolved relative to the config file."""

        return [(self.source_dir / library).resolve() for library in self.agent_libraries]

    def resolved_storage_path(self) -> Path:
        """Return storage path resolved relative to the config file."""

        return (self.source_dir / self.storage.path).resolve()
