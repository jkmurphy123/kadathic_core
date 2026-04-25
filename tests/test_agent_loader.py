from pathlib import Path

import pytest

from agent_foundry.agents.loader import AgentLoader
from agent_foundry.core.errors import AgentLoaderError


def write_agent(agent_dir: Path, personality_file: str = "personality.md") -> None:
    agent_dir.mkdir(parents=True)
    (agent_dir / "agent.yaml").write_text(
        f"""
id: test_agent
name: Test Agent
version: 0.1.0
description: Test description.
personality_file: {personality_file}
default_provider: mock
temperature: 0.2
""".strip(),
        encoding="utf-8",
    )


def test_loads_agent_definition_and_personality(tmp_path: Path) -> None:
    agent_dir = tmp_path / "agents" / "test_agent"
    write_agent(agent_dir)
    (agent_dir / "personality.md").write_text("Test personality.", encoding="utf-8")

    agent = AgentLoader().load(agent_dir)

    assert agent.id == "test_agent"
    assert agent.name == "Test Agent"
    assert agent.personality == "Test personality."
    assert agent.source_dir == agent_dir.resolve()
    assert agent.personality_path == (agent_dir / "personality.md").resolve()


def test_missing_personality_file_has_clear_error(tmp_path: Path) -> None:
    agent_dir = tmp_path / "agents" / "test_agent"
    write_agent(agent_dir, personality_file="missing.md")

    with pytest.raises(AgentLoaderError, match="Missing personality file"):
        AgentLoader().load(agent_dir)


def test_discovers_agent_directories(tmp_path: Path) -> None:
    library = tmp_path / "agents"
    first = library / "first"
    second = library / "second"
    write_agent(first)
    (first / "personality.md").write_text("First.", encoding="utf-8")
    write_agent(second)
    (second / "personality.md").write_text("Second.", encoding="utf-8")

    discovered = AgentLoader().discover(library)

    assert discovered == [first.resolve(), second.resolve()]
