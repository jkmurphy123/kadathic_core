# Agent Foundry Backend

Agent Foundry is a backend-first Python framework for defining, loading, and later
running reusable AI agents across applications. This repository currently implements
Milestone 8: example consumer apps.

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
- SQLite transcript storage.
- Recent session messages included in later context capsules.
- Session listing and transcript inspection.
- Ollama `/api/chat` provider support.
- Graceful Ollama server reachability checks through `providers health`.
- Provider smoke tests that send a real prompt through `providers smoke`.
- OpenAI-compatible `/v1/chat/completions` provider support.
- API key environment variable validation for OpenAI-compatible providers.
- Runnable consumer examples for plain chat, quiz context, and game context.
- Typer CLI commands:
  - `agentfoundry agents list`
  - `agentfoundry agents show AGENT_ID`
  - `agentfoundry providers list`
  - `agentfoundry providers health`
  - `agentfoundry context preview AGENT_ID --message "Hello"`
  - `agentfoundry chat AGENT_ID --message "Hello"`
  - `agentfoundry sessions list`
  - `agentfoundry sessions show SESSION_ID`

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
agentfoundry --config examples/sample_project/agentfoundry.yaml providers smoke ollama_local --prompt "Reply with exactly one word: pong"
agentfoundry --config examples/sample_project/agentfoundry.yaml context preview chat_companion --message "Hello"
agentfoundry --config examples/sample_project/agentfoundry.yaml chat chat_companion --message "Hello"
agentfoundry --config examples/sample_project/agentfoundry.yaml sessions list
agentfoundry --config examples/sample_project/agentfoundry.yaml sessions show cli-session
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

Runtime chat persists both the user message and assistant response to the SQLite
database configured by `storage.path` in `agentfoundry.yaml`. On later turns in the
same `project_id`, `agent_id`, `session_id`, and `user_id`, recent transcript messages
are loaded and included in the next context capsule.

## Ollama Provider

Add an Ollama provider to `agentfoundry.yaml`:

```yaml
providers:
  ollama_local:
    type: ollama
    base_url: http://localhost:11434
    model: qwen2.5-coder:7b
```

Agents can opt into it with:

```yaml
default_provider: ollama_local
```

`agentfoundry providers health` checks whether the Ollama server answers `/api/tags`.
That confirms the server is reachable, not that the configured model can generate.
Use this to send a real `/api/chat` prompt:

```bash
agentfoundry --config examples/sample_project/agentfoundry.yaml providers smoke ollama_local --prompt "Reply with exactly one word: pong"
```

If Ollama is not running, `providers health` reports an unavailable provider instead
of crashing. If the server is reachable but the model is missing or cannot generate,
`providers smoke` fails with the provider error.

## OpenAI-Compatible Provider

Add any `/v1/chat/completions` compatible endpoint to `agentfoundry.yaml`:

```yaml
providers:
  openai_compatible:
    type: openai_compatible
    base_url: https://api.example.test
    api_key_env: AGENT_FOUNDRY_OPENAI_COMPATIBLE_KEY
    model: example-chat-model
```

Set the configured environment variable before using the provider:

```bash
export AGENT_FOUNDRY_OPENAI_COMPATIBLE_KEY="..."
```

On PowerShell:

```powershell
$env:AGENT_FOUNDRY_OPENAI_COMPATIBLE_KEY = "..."
```

`providers health` checks that the API key environment variable is present.
`providers smoke openai_compatible --prompt "Hello"` sends a real chat completion
request.

## Example Consumers

These scripts show how non-GUI frontend apps call the backend. They default to the
configured local Ollama provider:

```bash
python examples/plain_chatbot.py --message "Hello"
python examples/quiz_context_demo.py --message "Can you give me a hint?"
python examples/game_context_demo.py --message "What should I try next?"
```

Use the mock provider for offline smoke tests:

```bash
python examples/plain_chatbot.py --provider mock --message "Hello"
```

## Tests

```bash
pytest
```

## Roadmap

The initial milestone roadmap is complete. Next likely work includes hardening
configuration overrides, improving provider diagnostics, and adding more consumer
templates or an HTTP service layer.
