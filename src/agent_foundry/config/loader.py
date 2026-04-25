"""Load project configuration from YAML."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from agent_foundry.config.models import ProjectConfig
from agent_foundry.core.errors import ConfigurationError


def load_project_config(path: Path | str) -> ProjectConfig:
    """Load and validate an `agentfoundry.yaml` file."""

    config_path = Path(path).expanduser().resolve()
    if not config_path.exists():
        raise ConfigurationError(f"Project config does not exist: {config_path}")

    data = _load_yaml(config_path)
    try:
        config = ProjectConfig.model_validate(data)
    except ValidationError as exc:
        raise ConfigurationError(f"Invalid project config in {config_path}: {exc}") from exc

    if config.default_provider not in config.providers:
        raise ConfigurationError(
            f"Default provider '{config.default_provider}' is not defined in providers."
        )

    return config.model_copy(update={"source_path": config_path})


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid project config YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigurationError(f"Project config must be a YAML mapping: {path}")
    return data
