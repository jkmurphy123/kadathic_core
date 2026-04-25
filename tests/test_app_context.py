from agent_foundry.context.app_context import AppContext
from agent_foundry.context.renderer import render_app_context


def test_render_minimal_app_context() -> None:
    app_context = AppContext.simple(
        app_id="plain_chat",
        app_type="chatbot",
        title="Plain Chat",
        state_summary="No special app state.",
    )

    rendered = render_app_context(app_context)

    assert "## Current App Context" in rendered
    assert "App: Plain Chat" in rendered
    assert "Type: chatbot" in rendered
    assert "Assist mode: companion" in rendered
    assert "Current state:\nNo special app state." in rendered


def test_render_rich_app_context() -> None:
    app_context = AppContext(
        app_id="game",
        app_type="game",
        title="Clockwork Atrium",
        assist_mode="hint_giver",
        state_summary="A brass gate blocks the west exit.",
        user_goal="Leave the atrium.",
        current_task="Open the gate.",
        visible_options=["Inspect pressure plate", "Use cracked gear"],
        recent_events=["The bronze key did not fit."],
        constraints=["Do not invent exits."],
    )

    rendered = render_app_context(app_context)

    assert "App: Clockwork Atrium" in rendered
    assert "User goal:\nLeave the atrium." in rendered
    assert "Current task:\nOpen the gate." in rendered
    assert "- Inspect pressure plate" in rendered
    assert "- The bronze key did not fit." in rendered
    assert "- Do not invent exits." in rendered
