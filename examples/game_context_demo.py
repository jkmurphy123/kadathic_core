"""Game context consumer example."""

from __future__ import annotations

import argparse
from pathlib import Path

from agent_foundry import AgentRuntime, AppContext

PROJECT_CONFIG = Path(__file__).parent / "sample_project" / "agentfoundry.yaml"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a game context example.")
    parser.add_argument("--message", default="What should I try next?")
    parser.add_argument("--session-id", default="example-game-context")
    parser.add_argument("--provider", default="ollama_local")
    args = parser.parse_args(argv)

    runtime = AgentRuntime.from_project_config(PROJECT_CONFIG)
    runtime.agent_registry.get("game_companion").default_provider = args.provider

    response = runtime.chat(
        agent_id="game_companion",
        project_id="demo_project",
        session_id=args.session_id,
        user_id="example-user",
        user_message=args.message,
        app_context=AppContext(
            app_id="game_demo",
            app_type="game",
            title="Clockwork Atrium",
            assist_mode="companion",
            state_summary=(
                "The player stands in the Clockwork Atrium. A locked brass gate "
                "blocks the west exit. The player carries a lantern and a cracked gear."
            ),
            user_goal="Find a way through the brass gate.",
            current_task="Investigate the gate mechanism.",
            visible_options=["Inspect pressure plate", "Use cracked gear", "Go east"],
            constraints=[
                "Do not invent exits, items, or mechanics.",
                "Treat current app context as authoritative.",
                "Offer hints before direct solutions.",
            ],
            recent_events=[
                "The player inspected the brass gate and saw a gear-shaped socket.",
                "The player tried the bronze key and it did not fit.",
            ],
        ),
    )

    print(response.text)


if __name__ == "__main__":
    main()
