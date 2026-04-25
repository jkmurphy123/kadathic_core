"""SQLite transcript storage."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from agent_foundry.providers.base import ProviderMessage
from agent_foundry.storage.sessions import SessionRecord, StoredMessage


class SQLiteSessionStore:
    """SQLite-backed session transcript store."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()

    def ensure_schema(self) -> None:
        """Create transcript tables if needed."""

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    context_capsule_id TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages (project_id, agent_id, session_id, user_id, id)
                """
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

        created_at = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO messages (
                    project_id,
                    agent_id,
                    session_id,
                    user_id,
                    role,
                    content,
                    context_capsule_id,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    agent_id,
                    session_id,
                    user_id,
                    role,
                    content,
                    context_capsule_id,
                    created_at,
                ),
            )

    def load_recent_messages(
        self,
        *,
        project_id: str,
        agent_id: str,
        session_id: str,
        user_id: str,
        limit: int,
    ) -> list[ProviderMessage]:
        """Load recent session messages in chronological order."""

        if limit <= 0:
            return []

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT role, content
                FROM (
                    SELECT id, role, content
                    FROM messages
                    WHERE project_id = ?
                      AND agent_id = ?
                      AND session_id = ?
                      AND user_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
                ORDER BY id ASC
                """,
                (project_id, agent_id, session_id, user_id, limit),
            ).fetchall()

        return [ProviderMessage(role=row["role"], content=row["content"]) for row in rows]

    def list_sessions(self, *, project_id: str | None = None) -> list[SessionRecord]:
        """List known sessions ordered by most recently updated."""

        query = """
            SELECT
                project_id,
                agent_id,
                session_id,
                user_id,
                COUNT(*) AS message_count,
                MIN(created_at) AS started_at,
                MAX(created_at) AS updated_at
            FROM messages
        """
        params: tuple[str, ...] = ()
        if project_id is not None:
            query += " WHERE project_id = ?"
            params = (project_id,)
        query += """
            GROUP BY project_id, agent_id, session_id, user_id
            ORDER BY updated_at DESC
        """

        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()

        return [self._session_from_row(row) for row in rows]

    def load_session_messages(
        self,
        *,
        session_id: str,
        project_id: str | None = None,
        agent_id: str | None = None,
        user_id: str | None = None,
    ) -> list[StoredMessage]:
        """Load transcript messages for a session."""

        clauses = ["session_id = ?"]
        params: list[str] = [session_id]
        if project_id is not None:
            clauses.append("project_id = ?")
            params.append(project_id)
        if agent_id is not None:
            clauses.append("agent_id = ?")
            params.append(agent_id)
        if user_id is not None:
            clauses.append("user_id = ?")
            params.append(user_id)

        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT *
                FROM messages
                WHERE {" AND ".join(clauses)}
                ORDER BY id ASC
                """,
                tuple(params),
            ).fetchall()

        return [self._message_from_row(row) for row in rows]

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _message_from_row(self, row: sqlite3.Row) -> StoredMessage:
        return StoredMessage(
            id=row["id"],
            project_id=row["project_id"],
            agent_id=row["agent_id"],
            session_id=row["session_id"],
            user_id=row["user_id"],
            role=row["role"],
            content=row["content"],
            context_capsule_id=row["context_capsule_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _session_from_row(self, row: sqlite3.Row) -> SessionRecord:
        return SessionRecord(
            project_id=row["project_id"],
            agent_id=row["agent_id"],
            session_id=row["session_id"],
            user_id=row["user_id"],
            message_count=row["message_count"],
            started_at=datetime.fromisoformat(row["started_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
