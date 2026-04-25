"""Agent Foundry command line interface."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from agent_foundry.agents.registry import AgentRegistry
from agent_foundry.config.loader import load_project_config
from agent_foundry.config.models import ProjectConfig
from agent_foundry.context.app_context import AppContext
from agent_foundry.context.manager import ContextManager
from agent_foundry.context.policy import ContextPolicy
from agent_foundry.core.errors import AgentFoundryError
from agent_foundry.core.runtime import AgentRuntime
from agent_foundry.providers.registry import ProviderRegistry
from agent_foundry.storage.sqlite import SQLiteSessionStore

app = typer.Typer(help="Agent Foundry backend CLI.")
agents_app = typer.Typer(help="Inspect reusable agents.")
providers_app = typer.Typer(help="Inspect configured providers.")
context_app = typer.Typer(help="Preview assembled context.")
sessions_app = typer.Typer(help="Inspect stored sessions.")
app.add_typer(agents_app, name="agents")
app.add_typer(providers_app, name="providers")
app.add_typer(context_app, name="context")
app.add_typer(sessions_app, name="sessions")
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


def _load_config() -> ProjectConfig:
    return load_project_config(state.config_path)


def _load_agent_registry() -> AgentRegistry:
    config = _load_config()
    enabled_agents = config.enabled_agents or None
    return AgentRegistry.from_libraries(
        config.resolved_agent_libraries(),
        enabled_agents=enabled_agents,
    )


def _load_provider_registry() -> ProviderRegistry:
    return ProviderRegistry.from_project_config(_load_config())


def _load_runtime() -> AgentRuntime:
    return AgentRuntime.from_project_config(state.config_path)


def _load_session_store() -> SQLiteSessionStore:
    return SQLiteSessionStore(_load_config().resolved_storage_path())


@agents_app.command("list")
def list_agents() -> None:
    """List enabled agents from the project config."""

    try:
        registry = _load_agent_registry()
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
        agent = _load_agent_registry().get(agent_id)
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


@providers_app.command("list")
def list_providers() -> None:
    """List providers from the project config."""

    try:
        config = _load_config()
        registry = ProviderRegistry.from_project_config(config)
    except AgentFoundryError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title="Providers")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Type")
    table.add_column("Model")
    table.add_column("Default")

    for provider in registry.list():
        provider_config = config.providers[provider.id]
        is_default = "yes" if provider.id == config.default_provider else ""
        table.add_row(provider.id, provider_config.type, provider_config.model or "", is_default)

    console.print(table)


@providers_app.command("health")
def provider_health() -> None:
    """Run health checks for configured providers."""

    try:
        registry = _load_provider_registry()
        health_results = [provider.health_check() for provider in registry.list()]
    except AgentFoundryError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title="Provider Health")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Healthy")
    table.add_column("Model")
    table.add_column("Message")

    for health in health_results:
        healthy = "yes" if health.healthy else "no"
        table.add_row(health.provider_id, healthy, health.model or "", health.message)

    console.print(table)


@app.command("chat")
def chat(
    agent_id: Annotated[str, typer.Argument(help="Agent id to chat with.")],
    message: Annotated[
        str | None,
        typer.Option("--message", "-m", help="Message to send. Prompts when omitted."),
    ] = None,
    session_id: Annotated[
        str,
        typer.Option("--session-id", help="Session id for this chat turn."),
    ] = "cli-session",
    user_id: Annotated[
        str,
        typer.Option("--user-id", help="User id for this chat turn."),
    ] = "cli-user",
    app_id: Annotated[
        str,
        typer.Option("--app-id", help="App id for generated context."),
    ] = "cli_chat",
    app_type: Annotated[
        str,
        typer.Option("--app-type", help="App type for generated context."),
    ] = "chatbot",
    state_summary: Annotated[
        str,
        typer.Option("--state-summary", help="State summary for generated context."),
    ] = "No special app state. This is a CLI chat turn.",
) -> None:
    """Send one chat turn to an agent."""

    user_message = message if message is not None else typer.prompt("Message")

    try:
        config = _load_config()
        runtime = _load_runtime()
        response = runtime.chat(
            agent_id=agent_id,
            project_id=config.project.id,
            session_id=session_id,
            user_id=user_id,
            user_message=user_message,
            app_context=AppContext.simple(
                app_id=app_id,
                app_type=app_type,
                state_summary=state_summary,
            ),
        )
    except AgentFoundryError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[bold]{agent_id}[/bold] via {response.provider_id}:")
    console.print(response.text, markup=False)
    console.print(f"Context capsule: {response.context_capsule_id}")


@context_app.command("preview")
def preview_context(
    agent_id: Annotated[str, typer.Argument(help="Agent id to preview.")],
    message: Annotated[
        str,
        typer.Option("--message", "-m", help="Current user message."),
    ] = "Hello",
    session_id: Annotated[
        str,
        typer.Option("--session-id", help="Session id for the preview capsule."),
    ] = "preview-session",
    user_id: Annotated[
        str,
        typer.Option("--user-id", help="User id for the preview capsule."),
    ] = "preview-user",
    app_id: Annotated[
        str,
        typer.Option("--app-id", help="App id for generated preview context."),
    ] = "preview_app",
    app_type: Annotated[
        str,
        typer.Option("--app-type", help="App type for generated preview context."),
    ] = "chatbot",
    state_summary: Annotated[
        str,
        typer.Option("--state-summary", help="State summary for generated preview context."),
    ] = "No special app state. This is a context preview.",
) -> None:
    """Preview the context capsule that would be sent to a provider."""

    try:
        config = _load_config()
        agent = _load_agent_registry().get(agent_id)
        app_context = AppContext.simple(
            app_id=app_id,
            app_type=app_type,
            state_summary=state_summary,
        )
        capsule = ContextManager().assemble(
            project_config=config,
            agent=agent,
            session_id=session_id,
            user_id=user_id,
            user_message=message,
            app_context=app_context,
            policy=ContextPolicy(
                include_app_context=True,
                max_recent_messages=config.context_policy.max_recent_messages,
                app_context_position=config.context_policy.app_context_position,
            ),
        )
    except AgentFoundryError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        Panel(
            f"Capsule ID: {capsule.id}\n"
            f"Project: {capsule.project_id}\n"
            f"Agent: {capsule.agent_id}\n"
            f"Session: {capsule.session_id}\n"
            f"User: {capsule.user_id}",
            title="Context Capsule",
        )
    )

    for index, rendered_message in enumerate(capsule.rendered_messages, start=1):
        console.print(
            Panel(
                Markdown(rendered_message.content),
                title=f"Rendered Message {index}: {rendered_message.role}",
            )
        )


@sessions_app.command("list")
def list_sessions() -> None:
    """List stored chat sessions."""

    try:
        config = _load_config()
        sessions = _load_session_store().list_sessions(project_id=config.project.id)
    except AgentFoundryError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title="Sessions")
    table.add_column("Session ID", style="cyan", no_wrap=True)
    table.add_column("Agent")
    table.add_column("User")
    table.add_column("Messages")
    table.add_column("Updated")

    for session in sessions:
        table.add_row(
            session.session_id,
            session.agent_id,
            session.user_id,
            str(session.message_count),
            session.updated_at.isoformat(timespec="seconds"),
        )

    console.print(table)


@sessions_app.command("show")
def show_session(
    session_id: Annotated[str, typer.Argument(help="Session id to show.")],
    agent_id: Annotated[
        str | None,
        typer.Option("--agent-id", help="Optional agent id filter."),
    ] = None,
    user_id: Annotated[
        str | None,
        typer.Option("--user-id", help="Optional user id filter."),
    ] = None,
) -> None:
    """Show transcript messages for a session."""

    try:
        config = _load_config()
        messages = _load_session_store().load_session_messages(
            project_id=config.project.id,
            agent_id=agent_id,
            session_id=session_id,
            user_id=user_id,
        )
    except AgentFoundryError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if not messages:
        console.print(f"No messages found for session: {session_id}")
        return

    for message in messages:
        title = (
            f"{message.role} | {message.agent_id} | "
            f"{message.created_at.isoformat(timespec='seconds')}"
        )
        console.print(f"[bold]{title}[/bold]")
        console.print(message.content, markup=False)


if __name__ == "__main__":
    app()
