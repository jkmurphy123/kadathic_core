"""Public package interface for Agent Foundry."""

from agent_foundry.core.errors import AgentFoundryError

__all__ = [
    "AgentDefinition",
    "AgentFoundryError",
    "AgentRegistry",
    "AgentRuntime",
    "AppContext",
    "ChatRequest",
    "ChatResponse",
    "ContextCapsule",
    "ContextManager",
    "MockProvider",
    "OllamaProvider",
    "OpenAICompatibleProvider",
    "ProjectConfig",
    "ProviderRegistry",
]


def __getattr__(name: str) -> object:
    """Lazily expose the public API without creating import cycles."""

    if name == "AgentDefinition":
        from agent_foundry.agents.definition import AgentDefinition

        return AgentDefinition
    if name == "AgentRegistry":
        from agent_foundry.agents.registry import AgentRegistry

        return AgentRegistry
    if name == "AgentRuntime":
        from agent_foundry.core.runtime import AgentRuntime

        return AgentRuntime
    if name == "AppContext":
        from agent_foundry.context.app_context import AppContext

        return AppContext
    if name == "ChatRequest":
        from agent_foundry.core.models import ChatRequest

        return ChatRequest
    if name == "ChatResponse":
        from agent_foundry.core.models import ChatResponse

        return ChatResponse
    if name == "ContextCapsule":
        from agent_foundry.context.capsule import ContextCapsule

        return ContextCapsule
    if name == "ContextManager":
        from agent_foundry.context.manager import ContextManager

        return ContextManager
    if name == "MockProvider":
        from agent_foundry.providers.mock import MockProvider

        return MockProvider
    if name == "OllamaProvider":
        from agent_foundry.providers.ollama import OllamaProvider

        return OllamaProvider
    if name == "OpenAICompatibleProvider":
        from agent_foundry.providers.openai_compatible import OpenAICompatibleProvider

        return OpenAICompatibleProvider
    if name == "ProjectConfig":
        from agent_foundry.config.models import ProjectConfig

        return ProjectConfig
    if name == "ProviderRegistry":
        from agent_foundry.providers.registry import ProviderRegistry

        return ProviderRegistry
    raise AttributeError(f"module 'agent_foundry' has no attribute {name!r}")
