"""Memory scope names reserved for current and future memory providers."""

from typing import Literal

MemoryScopeName = Literal[
    "session",
    "agent_project",
    "project",
    "agent_global",
    "user_global",
    "team",
]
