from typer.testing import CliRunner

from agent_foundry.cli.main import app

runner = CliRunner()


def test_chat_cli_with_mock_provider() -> None:
    result = runner.invoke(
        app,
        [
            "--config",
            "examples/sample_project/agentfoundry.yaml",
            "chat",
            "chat_companion",
            "--message",
            "Hello from CLI",
        ],
    )

    assert result.exit_code == 0
    assert "[mock:mock] Hello from CLI" in result.stdout
    assert "Context capsule:" in result.stdout
