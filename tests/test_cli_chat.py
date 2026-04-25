from pathlib import Path

from typer.testing import CliRunner

from agent_foundry.cli.main import app
from tests.helpers import write_temp_project_config

runner = CliRunner()


def test_chat_cli_with_mock_provider(tmp_path: Path) -> None:
    config_path = write_temp_project_config(tmp_path)

    result = runner.invoke(
        app,
        [
            "--config",
            str(config_path),
            "chat",
            "chat_companion",
            "--message",
            "Hello from CLI",
        ],
    )

    assert result.exit_code == 0
    assert "[mock:mock] Hello from CLI" in result.stdout
    assert "Context capsule:" in result.stdout
