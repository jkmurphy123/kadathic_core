# Agent Foundry Backend

Agent Foundry is a backend-first Python framework for defining, loading, and later
running reusable AI agents across applications. This repository currently implements
Milestone 4: runtime chat with the mock provider.

## Current Features

- Python package layout under `src/agent_foundry`.
- Pydantic `AgentDefinition` model.
- YAML agent definition loading.
- Personality markdown loading.
- In-memory `AgentRegistry`.
- Sample agents in `examples/agents`.
- Project config loading from `agentfoundry.yaml`.
- Provider registry.
- Deterministic mock provider.
- `AppContext` model for frontend-provided app state.
- Markdown rendering for app context.
- Inspectable `ContextCapsule` assembly.
- `AgentRuntime.from_project_config(...)`.
- End-to-end `runtime.chat(...)` with the deterministic mock provider.
- Typer CLI commands:
  - `agentfoundry agents list`
  - `agentfoundry agents show AGENT_ID`
  - `agentfoundry providers list`
  - `agentfoundry providers health`
  - `agentfoundry context preview AGENT_ID --message "Hello"`
  - `agentfoundry chat AGENT_ID --message "Hello"`

## Install

```bash
pip install -e ".[dev]"
```

## CLI Quickstart

```bash
agentfoundry --config examples/sample_project/agentfoundry.yaml agents list
agentfoundry --config examples/sample_project/agentfoundry.yaml agents show chat_companion
agentfoundry --config examples/sample_project/agentfoundry.yaml providers list
agentfoundry --config examples/sample_project/agentfoundry.yaml providers health
agentfoundry --config examples/sample_project/agentfoundry.yaml context preview chat_companion --message "Hello"
agentfoundry --config examples/sample_project/agentfoundry.yaml chat chat_companion --message "Hello"
```

## Agent Definition

Each agent lives in its own folder with `agent.yaml` and a personality markdown file:

```yaml
id: chat_companion
name: Chat Companion
version: 0.1.0
description: A simple companion for general chat.
personality_file: personality.md
default_provider: mock
temperature: 0.4
```

## Python Usage

```python
from agent_foundry import AgentRegistry, AgentRuntime
from agent_foundry.config import load_project_config
from agent_foundry.context import AppContext, ContextManager
from agent_foundry.providers import ProviderRegistry

config = load_project_config("examples/sample_project/agentfoundry.yaml")

agent_registry = AgentRegistry.from_libraries(config.resolved_agent_libraries())
agent = agent_registry.get("chat_companion")
print(agent.name)

provider_registry = ProviderRegistry.from_project_config(config)
provider = provider_registry.get(config.default_provider)
print(provider.health_check().message)

capsule = ContextManager().assemble(
    project_config=config,
    agent=agent,
    session_id="demo-session",
    user_id="local-user",
    user_message="Hello",
    app_context=AppContext.simple(
        app_id="plain_chat",
        app_type="chatbot",
        state_summary="No special app state.",
    ),
)
print(capsule.rendered_messages[-1].content)

runtime = AgentRuntime.from_project_config("examples/sample_project/agentfoundry.yaml")
response = runtime.chat(
    agent_id="chat_companion",
    project_id="demo_project",
    session_id="demo-session",
    user_id="local-user",
    user_message="Hello",
    app_context=AppContext.simple(
        app_id="plain_chat",
        app_type="chatbot",
        state_summary="No special app state.",
    ),
)
print(response.text)
```

## Tests

```bash
pytest
```

## Roadmap

Milestone 5 will add SQLite transcript storage, recent-message loading, session
listing, and session inspection.
