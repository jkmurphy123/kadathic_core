"""No-op memory manager for tests and future no-memory mode."""

from agent_foundry.providers.base import ProviderMessage


class NullMemoryManager:
    """Memory manager that never loads or saves messages."""

    def load_recent_messages(
        self,
        *,
        project_id: str,
        agent_id: str,
        session_id: str,
        user_id: str,
        limit: int,
    ) -> list[ProviderMessage]:
        """Return no recent messages."""

        return []

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
        """Ignore a transcript message."""

