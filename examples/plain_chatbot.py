"""Plain chatbot consumer example."""

from __future__ import annotations

import argparse
from pathlib import Path

from agent_foundry import AgentRuntime, AppContext

PROJECT_CONFIG = Path(__file__).parent / "sample_project" / "agentfoundry.yaml"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a plain chatbot example.")
    parser.add_argument("--message", default="Hello, how are you?")
    parser.add_argument("--session-id", default="example-plain-chatbot")
    parser.add_argument("--provider", default="ollama_local")
    args = parser.parse_args(argv)

    runtime = AgentRuntime.from_project_config(PROJECT_CONFIG)
    runtime.agent_registry.get("chat_companion").default_provider = args.provider

    response = runtime.chat(
        agent_id="chat_companion",
        project_id="demo_project",
        session_id=args.session_id,
        user_id="example-user",
        user_message=args.message,
        app_context=AppContext.simple(
            app_id="plain_chatbot_example",
            app_type="chatbot",
            title="Plain Chatbot",
            state_summary="No special app state. This is a plain chatbot session.",
        ),
    )

    print(response.text)


if __name__ == "__main__":
    main()
