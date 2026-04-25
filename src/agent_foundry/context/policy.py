"""Context assembly policy."""

from typing import Literal

from pydantic import BaseModel

AppContextPosition = Literal["before_user_message"]


class ContextPolicy(BaseModel):
    """Rules controlling context assembly."""

    include_app_context: bool = True
    max_recent_messages: int = 12
    app_context_position: AppContextPosition = "before_user_message"
