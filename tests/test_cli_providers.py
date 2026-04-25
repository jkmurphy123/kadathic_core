from typer.testing import CliRunner

from agent_foundry.cli.main import app

runner = CliRunner()


def test_providers_list_sample_project() -> None:
    result = runner.invoke(
        app,
        ["--config", "examples/sample_project/agentfoundry.yaml", "providers", "list"],
    )

    assert result.exit_code == 0
    assert "mock" in result.stdout
    assert "mock-model" in result.stdout
    assert "yes" in result.stdout


def test_providers_health_sample_project() -> None:
    result = runner.invoke(
        app,
        ["--config", "examples/sample_project/agentfoundry.yaml", "providers", "health"],
    )

    assert result.exit_code == 0
    assert "mock" in result.stdout
    assert "Mock provider is available." in result.stdout
