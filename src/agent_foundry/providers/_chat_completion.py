"""Shared helpers for OpenAI-compatible chat completion providers."""

from typing import Any


def _text_from_chat_completion(data: dict[str, Any]) -> str:
    """Extract the assistant message text from a chat completion response."""
    choices = data.get("choices", [])
    if not isinstance(choices, list) or not choices:
        return ""

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return ""

    message = first_choice.get("message", {})
    if not isinstance(message, dict):
        return ""

    content = message.get("content")
    return content if isinstance(content, str) else ""
