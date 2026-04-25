"""Markdown renderers for context inputs."""

from agent_foundry.context.app_context import AppContext


def render_app_context(app_context: AppContext) -> str:
    """Render app context as a clear markdown section."""

    lines = [
        "## Current App Context",
        "",
        f"App: {app_context.title or app_context.app_id}",
        f"Type: {app_context.app_type}",
        f"Assist mode: {app_context.assist_mode}",
        f"Allowed knowledge: {app_context.allowed_knowledge}",
        "",
        "Current state:",
        app_context.state_summary,
    ]

    if app_context.user_goal:
        lines.extend(["", "User goal:", app_context.user_goal])

    if app_context.current_task:
        lines.extend(["", "Current task:", app_context.current_task])

    _extend_bullets(lines, "Visible options", app_context.visible_options)
    _extend_bullets(lines, "Recent events", app_context.recent_events)
    _extend_bullets(lines, "Constraints", app_context.constraints)

    return "\n".join(lines).strip()


def _extend_bullets(lines: list[str], title: str, values: list[str]) -> None:
    if not values:
        return

    lines.extend(["", f"{title}:"])
    lines.extend(f"- {value}" for value in values)
