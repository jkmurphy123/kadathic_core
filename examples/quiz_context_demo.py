"""Quiz context consumer example."""

from __future__ import annotations

import argparse
from pathlib import Path

from agent_foundry import AgentRuntime, AppContext

PROJECT_CONFIG = Path(__file__).parent / "sample_project" / "agentfoundry.yaml"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a quiz context example.")
    parser.add_argument("--message", default="Can you give me a hint?")
    parser.add_argument("--session-id", default="example-quiz-context")
    parser.add_argument("--provider", default="ollama_local")
    args = parser.parse_args(argv)

    runtime = AgentRuntime.from_project_config(PROJECT_CONFIG)
    runtime.agent_registry.get("quiz_tutor").default_provider = args.provider

    response = runtime.chat(
        agent_id="quiz_tutor",
        project_id="demo_project",
        session_id=args.session_id,
        user_id="example-user",
        user_message=args.message,
        app_context=AppContext(
            app_id="quiz_demo",
            app_type="quiz",
            title="World Capitals Quiz",
            assist_mode="hint_giver",
            state_summary=(
                "Question: Which city is the capital of Canada? "
                "Choices: Toronto, Ottawa, Vancouver, Montreal."
            ),
            user_goal="Answer the current quiz question correctly.",
            current_task="Choose one of the visible options.",
            visible_options=["Toronto", "Ottawa", "Vancouver", "Montreal"],
            constraints=[
                "Give a hint before the direct answer.",
                "Do not mention hidden answer keys unless allowed by context.",
            ],
            recent_events=["The user has not answered this question yet."],
        ),
    )

    print(response.text)


if __name__ == "__main__":
    main()
