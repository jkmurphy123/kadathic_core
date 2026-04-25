from typer.testing import CliRunner

from agent_foundry.cli.main import app

runner = CliRunner()


def test_context_preview_sample_agent() -> None:
    result = runner.invoke(
        app,
        [
            "--config",
            "examples/sample_project/agentfoundry.yaml",
            "context",
            "preview",
            "chat_companion",
            "--message",
            "Hello",
        ],
    )

    assert result.exit_code == 0
    assert "Context Capsule" in result.stdout
    assert "Agent Personality" in result.stdout
    assert "Current App Context" in result.stdout
    assert "Current User Message" in result.stdout
    assert "Hello" in result.stdout
