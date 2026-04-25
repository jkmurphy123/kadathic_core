"""Application context model supplied by host frontends."""

from typing import Any, Literal

from pydantic import BaseModel, Field

AssistMode = Literal[
    "companion",
    "hint_giver",
    "tutor",
    "referee",
    "spoiler_allowed",
    "debug",
]

AllowedKnowledge = Literal[
    "player_visible_only",
    "answer_key_allowed",
    "director_notes_allowed",
    "debug_full_state",
]


class AppContext(BaseModel):
    """Current app, game, or task state for one agent turn."""

    app_id: str
    app_type: str
    title: str | None = None
    assist_mode: AssistMode = "companion"
    allowed_knowledge: AllowedKnowledge = "player_visible_only"

    state_summary: str

    user_goal: str | None = None
    current_task: str | None = None
    visible_options: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    recent_events: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def simple(
        cls,
        app_id: str,
        app_type: str,
        state_summary: str,
        title: str | None = None,
        assist_mode: AssistMode = "companion",
    ) -> "AppContext":
        """Create a minimal app context."""

        return cls(
            app_id=app_id,
            app_type=app_type,
            title=title,
            state_summary=state_summary,
            assist_mode=assist_mode,
        )
