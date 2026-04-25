"""Core framework primitives."""

__all__ = ["AgentRuntime", "ChatRequest", "ChatResponse"]


def __getattr__(name: str) -> object:
    """Lazily expose core public objects."""

    if name == "AgentRuntime":
        from agent_foundry.core.runtime import AgentRuntime

        return AgentRuntime
    if name == "ChatRequest":
        from agent_foundry.core.models import ChatRequest

        return ChatRequest
    if name == "ChatResponse":
        from agent_foundry.core.models import ChatResponse

        return ChatResponse
    raise AttributeError(f"module 'agent_foundry.core' has no attribute {name!r}")
