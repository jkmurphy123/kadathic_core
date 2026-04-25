"""In-memory registry for loaded agents."""

from collections.abc import Iterable
from pathlib import Path

from agent_foundry.agents.definition import AgentDefinition
from agent_foundry.agents.loader import AgentLoader
from agent_foundry.core.errors import AgentLoaderError, AgentNotFoundError


class AgentRegistry:
    """Stores loaded agent definitions by id."""

    def __init__(self, agents: Iterable[AgentDefinition] | None = None) -> None:
        self._agents: dict[str, AgentDefinition] = {}
        for agent in agents or []:
            self.register(agent)

    @classmethod
    def from_libraries(
        cls,
        library_paths: Iterable[Path | str],
        enabled_agents: Iterable[str] | None = None,
        loader: AgentLoader | None = None,
    ) -> "AgentRegistry":
        """Load all agents from one or more library directories."""

        active_loader = loader or AgentLoader()
        enabled = set(enabled_agents) if enabled_agents is not None else None
        registry = cls()

        for library_path in library_paths:
            for agent_dir in active_loader.discover(library_path):
                agent = active_loader.load(agent_dir)
                if enabled is None or agent.id in enabled:
                    registry.register(agent)

        if enabled is not None:
            missing = enabled.difference(registry.ids())
            if missing:
                missing_text = ", ".join(sorted(missing))
                raise AgentLoaderError(f"Enabled agents were not found: {missing_text}")

        return registry

    def register(self, agent: AgentDefinition) -> None:
        """Register an agent definition."""

        if agent.id in self._agents:
            raise AgentLoaderError(f"Duplicate agent id: {agent.id}")
        self._agents[agent.id] = agent

    def get(self, agent_id: str) -> AgentDefinition:
        """Return an agent by id."""

        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise AgentNotFoundError(f"Agent not found: {agent_id}") from exc

    def list(self) -> list[AgentDefinition]:
        """Return all agents sorted by id."""

        return [self._agents[key] for key in sorted(self._agents)]

    def ids(self) -> set[str]:
        """Return all registered agent ids."""

        return set(self._agents)
