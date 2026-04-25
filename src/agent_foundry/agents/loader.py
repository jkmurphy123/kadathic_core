"""Load agent definitions and personality markdown from disk."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from agent_foundry.agents.definition import AgentDefinition
from agent_foundry.config.loader import load_project_config
from agent_foundry.core.errors import AgentLoaderError


class AgentLoader:
    """Loads one agent folder containing `agent.yaml` and personality markdown."""

    definition_filename = "agent.yaml"

    def load(self, agent_dir: Path | str) -> AgentDefinition:
        """Load and validate an agent definition from an agent directory."""

        source_dir = Path(agent_dir).expanduser().resolve()
        definition_path = source_dir / self.definition_filename
        if not definition_path.exists():
            raise AgentLoaderError(f"Missing agent definition file: {definition_path}")

        raw_data = self._load_yaml(definition_path)
        try:
            definition = AgentDefinition.model_validate(raw_data)
        except ValidationError as exc:
            raise AgentLoaderError(
                f"Invalid agent definition in {definition_path}: {exc}"
            ) from exc

        personality_path = (source_dir / definition.personality_file).resolve()
        if not personality_path.exists():
            raise AgentLoaderError(
                f"Missing personality file for agent '{definition.id}': {personality_path}"
            )

        return definition.model_copy(
            update={
                "source_dir": source_dir,
                "personality_path": personality_path,
                "personality": personality_path.read_text(encoding="utf-8").strip(),
            }
        )

    def discover(self, library_dir: Path | str) -> list[Path]:
        """Discover agent directories below a library path."""

        root = Path(library_dir).expanduser().resolve()
        if not root.exists():
            raise AgentLoaderError(f"Agent library does not exist: {root}")

        if (root / self.definition_filename).exists():
            return [root]

        agent_dirs = [
            path.parent
            for path in sorted(root.glob(f"*/{self.definition_filename}"))
            if path.is_file()
        ]
        return agent_dirs

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise AgentLoaderError(f"Invalid YAML in {path}: {exc}") from exc

        if not isinstance(data, dict):
            raise AgentLoaderError(f"Agent definition must be a YAML mapping: {path}")
        return data


def load_agent_config(path: Path | str) -> tuple[list[Path], list[str] | None]:
    """Load agent library settings from `agentfoundry.yaml`."""

    config = load_project_config(path)
    enabled_agents = config.enabled_agents or None
    return config.resolved_agent_libraries(), enabled_agents
