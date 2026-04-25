"""Memory manager backed by local transcript storage."""

from agent_foundry.providers.base import ProviderMessage
from agent_foundry.storage.sqlite import SQLiteSessionStore


class MemoryManager:
    """Loads and saves session-scoped transcript messages."""

    def __init__(self, store: SQLiteSessionStore) -> None:
        self.store = store

    def load_recent_messages(
        self,
        *,
        project_id: str,
        agent_id: str,
        session_id: str,
        user_id: str,
        limit: int,
    ) -> list[ProviderMessage]:
        """Load recent messages for a session."""

        return self.store.load_recent_messages(
            project_id=project_id,
            agent_id=agent_id,
            session_id=session_id,
            user_id=user_id,
            limit=limit,
        )

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

        self.store.save_message(
            project_id=project_id,
            agent_id=agent_id,
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            context_capsule_id=context_capsule_id,
        )
