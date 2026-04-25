"""Session storage models."""

from datetime import datetime

from pydantic import BaseModel


class StoredMessage(BaseModel):
    """Transcript message loaded from storage."""

    id: int
    project_id: str
    agent_id: str
    session_id: str
    user_id: str
    role: str
    content: str
    context_capsule_id: str | None = None
    created_at: datetime


class SessionRecord(BaseModel):
    """Session summary loaded from storage."""

    project_id: str
    agent_id: str
    session_id: str
    user_id: str
    message_count: int
    started_at: datetime
    updated_at: datetime
