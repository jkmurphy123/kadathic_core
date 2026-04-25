# Agent Foundry Backend

Agent Foundry is a backend-first Python framework for defining, loading, and later
running reusable AI agents across applications. This repository currently implements
Milestone 2: project configuration and provider registry.

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
- Typer CLI commands:
  - `agentfoundry agents list`
  - `agentfoundry agents show AGENT_ID`
  - `agentfoundry providers list`
  - `agentfoundry providers health`

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
from agent_foundry import AgentRegistry
from agent_foundry.config import load_project_config
from agent_foundry.providers import ProviderRegistry

config = load_project_config("examples/sample_project/agentfoundry.yaml")

agent_registry = AgentRegistry.from_libraries(config.resolved_agent_libraries())
agent = agent_registry.get("chat_companion")
print(agent.name)

provider_registry = ProviderRegistry.from_project_config(config)
provider = provider_registry.get(config.default_provider)
print(provider.health_check().message)
```

## Tests

```bash
pytest
```

## Roadmap

Milestone 3 will add `AppContext`, context policy models, context capsule assembly,
and context preview support. Runtime chat and SQLite memory follow in later
milestones.
