from typer.testing import CliRunner

from agent_foundry.cli.main import app

runner = CliRunner()


def test_agents_list_sample_project() -> None:
    result = runner.invoke(
        app,
        ["--config", "examples/sample_project/agentfoundry.yaml", "agents", "list"],
    )

    assert result.exit_code == 0
    assert "chat_companion" in result.stdout
    assert "quiz_tutor" in result.stdout
    assert "game_companion" in result.stdout


def test_agents_show_sample_agent() -> None:
    result = runner.invoke(
        app,
        [
            "--config",
            "examples/sample_project/agentfoundry.yaml",
            "agents",
            "show",
            "chat_companion",
        ],
    )

    assert result.exit_code == 0
    assert "Chat Companion" in result.stdout
    assert "personality.md" in result.stdout
