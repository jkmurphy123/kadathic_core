from pathlib import Path

import pytest

from agent_foundry.config.loader import load_project_config
from agent_foundry.core.errors import ConfigurationError


def test_loads_sample_project_config() -> None:
    config = load_project_config("examples/sample_project/agentfoundry.yaml")

    assert config.project.id == "demo_project"
    assert config.default_provider == "ollama_local"
    assert config.providers["mock"].type == "mock"
    assert config.providers["mock"].model == "mock-model"
    assert config.resolved_agent_libraries() == [
        (Path("examples/sample_project") / "../agents").resolve()
    ]


def test_missing_default_provider_has_clear_error(tmp_path: Path) -> None:
    config_path = tmp_path / "agentfoundry.yaml"
    config_path.write_text(
        """
project:
  id: demo
default_provider: missing
providers:
  mock:
    type: mock
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Default provider 'missing'"):
        load_project_config(config_path)


def test_invalid_provider_type_has_clear_error(tmp_path: Path) -> None:
    config_path = tmp_path / "agentfoundry.yaml"
    config_path.write_text(
        """
project:
  id: demo
default_provider: bad
providers:
  bad:
    type: unsupported
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Invalid project config"):
        load_project_config(config_path)
