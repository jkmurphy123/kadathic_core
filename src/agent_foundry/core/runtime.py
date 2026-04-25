"""Agent runtime for end-to-end chat calls."""

from pathlib import Path

from agent_foundry.agents.definition import AgentDefinition
from agent_foundry.agents.registry import AgentRegistry
from agent_foundry.config.loader import load_project_config
from agent_foundry.config.models import ProjectConfig
from agent_foundry.context.app_context import AppContext
from agent_foundry.context.manager import ContextManager
from agent_foundry.core.errors import ConfigurationError
from agent_foundry.core.models import ChatResponse
from agent_foundry.memory.manager import MemoryManager
from agent_foundry.memory.null import NullMemoryManager
from agent_foundry.providers.base import ProviderChatRequest
from agent_foundry.providers.registry import ProviderRegistry
from agent_foundry.storage.sqlite import SQLiteSessionStore


class AgentRuntime:
    """Coordinates agents, context assembly, and provider calls."""

    def __init__(
        self,
        *,
        project_config: ProjectConfig,
        agent_registry: AgentRegistry,
        provider_registry: ProviderRegistry,
        context_manager: ContextManager | None = None,
        memory_manager: MemoryManager | NullMemoryManager | None = None,
    ) -> None:
        self.project_config = project_config
        self.agent_registry = agent_registry
        self.provider_registry = provider_registry
        self.context_manager = context_manager or ContextManager()
        self.memory_manager = memory_manager or MemoryManager(
            SQLiteSessionStore(project_config.resolved_storage_path())
        )

    @classmethod
    def from_project_config(cls, config_path: Path | str) -> "AgentRuntime":
        """Create a runtime from an `agentfoundry.yaml` file."""

        project_config = load_project_config(config_path)
        enabled_agents = project_config.enabled_agents or None
        agent_registry = AgentRegistry.from_libraries(
            project_config.resolved_agent_libraries(),
            enabled_agents=enabled_agents,
        )
        provider_registry = ProviderRegistry.from_project_config(project_config)
        return cls(
            project_config=project_config,
            agent_registry=agent_registry,
            provider_registry=provider_registry,
        )

    def chat(
        self,
        *,
        agent_id: str,
        project_id: str,
        session_id: str,
        user_id: str,
        user_message: str,
        app_context: AppContext | None = None,
    ) -> ChatResponse:
        """Run one chat turn with an agent."""

        agent = self.agent_registry.get(agent_id)
        provider_id = self._provider_id_for_agent(agent)
        provider = self.provider_registry.get(provider_id)
        recent_messages = self.memory_manager.load_recent_messages(
            project_id=project_id,
            agent_id=agent_id,
            session_id=session_id,
            user_id=user_id,
            limit=self.project_config.context_policy.max_recent_messages,
        )
        capsule = self.context_manager.assemble(
            project_config=self.project_config,
            agent=agent,
            project_id=project_id,
            session_id=session_id,
            user_id=user_id,
            user_message=user_message,
            app_context=app_context,
            recent_messages=recent_messages,
        )
        provider_response = provider.chat(
            ProviderChatRequest(
                messages=capsule.rendered_messages,
                model=self._model_for_provider(provider_id),
                temperature=agent.temperature,
                metadata={"context_capsule_id": capsule.id},
            )
        )
        self.memory_manager.save_message(
            project_id=project_id,
            agent_id=agent.id,
            session_id=session_id,
            user_id=user_id,
            role="user",
            content=user_message,
            context_capsule_id=capsule.id,
        )
        self.memory_manager.save_message(
            project_id=project_id,
            agent_id=agent.id,
            session_id=session_id,
            user_id=user_id,
            role="assistant",
            content=provider_response.text,
            context_capsule_id=capsule.id,
        )

        return ChatResponse(
            text=provider_response.text,
            agent_id=agent.id,
            session_id=session_id,
            provider_id=provider_response.provider_id,
            model=provider_response.model,
            context_capsule_id=capsule.id,
            usage=provider_response.usage,
            metadata={
                **provider_response.metadata,
                "project_id": project_id,
            },
        )

    def _provider_id_for_agent(self, agent: AgentDefinition) -> str:
        provider_id = agent.default_provider or self.project_config.default_provider
        if provider_id not in self.provider_registry.ids():
            raise ConfigurationError(
                f"Provider '{provider_id}' for agent '{agent.id}' is not configured."
            )
        return provider_id

    def _model_for_provider(self, provider_id: str) -> str | None:
        provider_config = self.project_config.providers.get(provider_id)
        if provider_config is None:
            return None
        return provider_config.model
