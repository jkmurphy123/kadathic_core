# Agent Foundry Backend

Agent Foundry is a backend-first Python framework for defining, loading, and later
running reusable AI agents across applications. This repository currently implements
Milestone 1: project skeleton and agent loading.

## Current Features

- Python package layout under `src/agent_foundry`.
- Pydantic `AgentDefinition` model.
- YAML agent definition loading.
- Personality markdown loading.
- In-memory `AgentRegistry`.
- Sample agents in `examples/agents`.
- Typer CLI commands:
  - `agentfoundry agents list`
  - `agentfoundry agents show AGENT_ID`

## Install

```bash
pip install -e ".[dev]"
```

## CLI Quickstart

```bash
agentfoundry --config examples/sample_project/agentfoundry.yaml agents list
agentfoundry --config examples/sample_project/agentfoundry.yaml agents show chat_companion
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

registry = AgentRegistry.from_libraries(["examples/agents"])
agent = registry.get("chat_companion")

print(agent.name)
print(agent.personality)
```

## Tests

```bash
pytest
```

## Roadmap

Milestone 2 will add project configuration models, provider registry support, and a
deterministic mock provider. Runtime chat, context capsules, and SQLite memory follow
in later milestones.
