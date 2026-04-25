"""Memory manager protocol."""

from typing import Protocol

from agent_foundry.providers.base import ProviderMessage


class MemoryBackend(Protocol):
    """Protocol for short-term memory backends."""

    def load_recent_messages(
        self,
        *,
        project_id: str,
        agent_id: str,
        session_id: str,
        user_id: str,
        limit: int,
    ) -> list[ProviderMessage]:
        """Load recent session messages."""

    def save_message(
        self,
        *,
        project_id: str,
        agent_id: str,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        context_capsule_id: str | None = None,
    ) -> None:
        """Save one transcript message."""
