from pathlib import Path

from typer.testing import CliRunner

from agent_foundry.cli.main import app
from tests.helpers import write_temp_project_config

runner = CliRunner()


def test_sessions_cli_lists_and_shows_chat_transcript(tmp_path: Path) -> None:
    config_path = write_temp_project_config(tmp_path)

    chat_result = runner.invoke(
        app,
        [
            "--config",
            str(config_path),
            "chat",
            "chat_companion",
            "--session-id",
            "session-001",
            "--message",
            "Hello sessions",
        ],
    )
    list_result = runner.invoke(app, ["--config", str(config_path), "sessions", "list"])
    show_result = runner.invoke(
        app,
        ["--config", str(config_path), "sessions", "show", "session-001"],
    )

    assert chat_result.exit_code == 0
    assert list_result.exit_code == 0
    assert "session-001" in list_result.stdout
    assert "2" in list_result.stdout
    assert show_result.exit_code == 0
    assert "Hello sessions" in show_result.stdout
    assert "[mock:mock] Hello sessions" in show_result.stdout
