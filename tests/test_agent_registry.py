from pathlib import Path

import pytest

from agent_foundry.agents.definition import AgentDefinition
from agent_foundry.agents.registry import AgentRegistry
from agent_foundry.core.errors import AgentLoaderError, AgentNotFoundError


def test_registry_returns_agents_sorted_by_id() -> None:
    registry = AgentRegistry(
        [
            AgentDefinition(id="z_agent", name="Z", version="0.1.0", description="Z"),
            AgentDefinition(id="a_agent", name="A", version="0.1.0", description="A"),
        ]
    )

    assert [agent.id for agent in registry.list()] == ["a_agent", "z_agent"]


def test_registry_rejects_duplicate_ids() -> None:
    registry = AgentRegistry()
    registry.register(AgentDefinition(id="agent", name="A", version="0.1.0", description="A"))

    with pytest.raises(AgentLoaderError, match="Duplicate agent id"):
        registry.register(AgentDefinition(id="agent", name="B", version="0.1.0", description="B"))


def test_registry_raises_for_unknown_agent() -> None:
    with pytest.raises(AgentNotFoundError, match="Agent not found"):
        AgentRegistry().get("missing")


def test_registry_loads_enabled_agents_from_library(tmp_path: Path) -> None:
    library = tmp_path / "agents"
    for agent_id in ("one", "two"):
        agent_dir = library / agent_id
        agent_dir.mkdir(parents=True)
        (agent_dir / "agent.yaml").write_text(
            f"""
id: {agent_id}
name: {agent_id.title()}
version: 0.1.0
description: Example.
personality_file: personality.md
""".strip(),
            encoding="utf-8",
        )
        (agent_dir / "personality.md").write_text(f"{agent_id} personality.", encoding="utf-8")

    registry = AgentRegistry.from_libraries([library], enabled_agents=["two"])

    assert registry.ids() == {"two"}
