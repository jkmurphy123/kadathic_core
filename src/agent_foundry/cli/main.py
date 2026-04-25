"""Agent Foundry command line interface."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from agent_foundry.agents.loader import load_agent_config
from agent_foundry.agents.registry import AgentRegistry
from agent_foundry.core.errors import AgentFoundryError

app = typer.Typer(help="Agent Foundry backend CLI.")
agents_app = typer.Typer(help="Inspect reusable agents.")
app.add_typer(agents_app, name="agents")
console = Console(width=160)


class CliState:
    """Mutable CLI state shared by subcommands."""

    def __init__(self) -> None:
        self.config_path = Path("examples/sample_project/agentfoundry.yaml")


state = CliState()


@app.callback()
def main(
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            "-c",
            help="Path to agentfoundry.yaml.",
        ),
    ] = Path("examples/sample_project/agentfoundry.yaml"),
) -> None:
    """Configure the CLI."""

    state.config_path = config


def _load_registry() -> AgentRegistry:
    libraries, enabled_agents = load_agent_config(state.config_path)
    return AgentRegistry.from_libraries(libraries, enabled_agents=enabled_agents)


@agents_app.command("list")
def list_agents() -> None:
    """List enabled agents from the project config."""

    try:
        registry = _load_registry()
    except AgentFoundryError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title="Agents")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Version")
    table.add_column("Description")

    for agent in registry.list():
        table.add_row(agent.id, agent.name, agent.version, agent.description)

    console.print(table)


@agents_app.command("show")
def show_agent(agent_id: Annotated[str, typer.Argument(help="Agent id to show.")]) -> None:
    """Show metadata for one agent."""

    try:
        agent = _load_registry().get(agent_id)
    except AgentFoundryError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[bold]{agent.name}[/bold] ({agent.id})")
    console.print(f"Version: {agent.version}")
    console.print(f"Description: {agent.description}")
    console.print(f"Default provider: {agent.default_provider or 'not set'}")
    temperature = agent.temperature if agent.temperature is not None else "not set"
    console.print(f"Temperature: {temperature}")
    console.print(f"Personality file: {agent.personality_file}")
    console.print(f"Source: {agent.source_dir}")
    console.print(f"Personality: {agent.personality_path}")


if __name__ == "__main__":
    app()
