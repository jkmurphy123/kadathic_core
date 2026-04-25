# Agent Foundry Backend Design Brief

## 1. Overview

Agent Foundry is a reusable Python backend framework for AI-powered applications. Its job is to let different apps reuse a common set of agents, personalities, providers, memory systems, and context-management behavior.

The immediate goal is to support future NiceGUI frontend templates, including:

1. A simple chatbot shell.
2. A split-panel app with a task/game area and agent chat.
3. A quiz app with a hint/tutor agent.
4. A game app with a companion/referee agent.
5. A developer workbench for inspecting context and memory.

This repository should build only the backend foundation.

---

## 2. Problem Statement

Many AI app experiments repeat the same code:

- Provider wiring
- Agent personality loading
- Prompt assembly
- Session history
- Memory handling
- Context injection
- Debug logging
- Agent selection
- Model/provider selection

Agent Foundry should provide these reusable pieces so each new project can simply drop in an agent and give it app-specific context.

---

## 3. Core Concept

A frontend app should be able to say:

> “Here is the user’s message. Here is the current app state. Use this agent. Continue this session.”

The backend should handle:

- Loading the agent personality
- Loading project rules
- Loading recent conversation
- Loading relevant memory
- Rendering app context
- Building a provider-neutral chat request
- Calling the provider
- Saving the transcript
- Returning a response

---

## 4. High-Level Architecture

```text
Frontend App
  |
  | runtime.chat(...)
  v
AgentRuntime
  |
  +-- AgentRegistry
  |     loads reusable agents and personality markdown
  |
  +-- ConfigManager
  |     loads project config and provider config
  |
  +-- ContextManager
  |     builds ContextCapsule
  |
  +-- MemoryManager
  |     loads/saves session history and future long-term memory
  |
  +-- ProviderRegistry
  |     resolves provider adapter
  |
  +-- ProviderAdapter
        calls Mock/Ollama/OpenAI-compatible/OpenClaw later
```

---

## 5. Key Design Objects

### 5.1 AgentDefinition

Represents a reusable agent.

Fields:

- `id`
- `name`
- `version`
- `description`
- `personality_file`
- `default_provider`
- `temperature`
- `memory`
- `context_policy`
- `metadata`

Each agent lives in its own folder:

```text
agents/
  chat_companion/
    agent.yaml
    personality.md
```

---

### 5.2 AppContext

Represents the app/game/task state provided by the frontend for a single agent turn.

Required fields:

- `app_id`
- `app_type`
- `state_summary`

Optional fields:

- `title`
- `assist_mode`
- `allowed_knowledge`
- `user_goal`
- `current_task`
- `visible_options`
- `constraints`
- `recent_events`
- `metadata`

The frontend owns the truth of the app state. Agent Foundry owns how that state is rendered into the agent context.

---

### 5.3 ContextCapsule

A complete, inspectable context packet for one agent turn.

It includes:

- IDs: user/project/agent/session
- system instructions
- agent personality
- project context
- memory context
- recent messages
- optional app context
- current user message
- final rendered provider messages

This should be easy to preview in the CLI.

---

### 5.4 ProviderAdapter

A provider adapter hides LLM backend details.

Initial providers:

- Mock provider
- Ollama provider
- OpenAI-compatible provider

Future providers:

- OpenClaw Gateway
- Claude-compatible provider
- Local llama.cpp server
- Other OpenAI-compatible endpoints

---

### 5.5 MemoryManager

Initial memory should be simple and local:

- SQLite transcripts
- Load recent session messages
- Save user and assistant turns
- List sessions
- Show sessions

Future memory providers:

- LlamaIndex Memory
- LangGraph checkpointing
- Zep
- Mem0
- pgvector
- Qdrant
- Chroma

---

## 6. Context Model

The framework should treat context as layered sections, not a single blob.

Suggested rendering order:

1. System instructions
2. Agent personality
3. Project rules
4. Memory context
5. Session summary
6. Recent conversation
7. App context
8. Current user message

Current `AppContext` should be treated as authoritative for current app/game/task state.

If old session history conflicts with current app state, current app state wins.

---

## 7. AppContext Rendering

A rich app context may render like this:

```text
## Current App Context

App: Champions of the Proving Depths
Type: game
Assist mode: companion
Allowed knowledge: player_visible_only

Current state:
The player is in the Clockwork Atrium. A locked brass gate blocks the west exit.
The player carries a lantern and a cracked gear.

Current task:
Find a way through the brass gate.

Visible options:
- Inspect pressure plate
- Use cracked gear
- Go east

Recent events:
- The player inspected the brass gate and saw a gear-shaped socket.
- The player tried the bronze key and it did not fit.

Constraints:
- Do not invent exits, items, or mechanics not present in the state summary.
- Offer hints before direct solutions.
```

A minimal chatbot context may render like this:

```text
## Current App Context

App: Plain Chat
Type: chatbot
Assist mode: companion

Current state:
No special app state. This is a plain chatbot session.
```

---

## 8. Frontend Template Roadmap

These are not part of the backend repo yet, but the backend should support them.

### Template 0: Chatbot Shell

Purpose:

- Test agent loading.
- Test personality markdown.
- Test provider selection.
- Test short-term memory.
- Test transcript persistence.

AppContext:

- Optional.
- Usually app_type `chatbot`.

Layout later in NiceGUI:

```text
Top bar: agent selector, provider selector, new session
Main: chat window
Bottom bar: provider/model/session status
```

---

### Template 1: Split App + Agent

Purpose:

- Test app context injection.

AppContext:

- Required.
- State summary describes a fake task or scenario.

Layout:

```text
Left: app/task panel
Right: agent chat
Bottom: status/context preview button
```

---

### Template 2: Quiz + Hint Agent

Purpose:

- Test assist modes.
- Test current task, visible options, and constraints.

AppContext:

- app_type `quiz`
- assist_mode `hint_giver`
- current question
- choices
- recent results
- constraints like “hint first”

---

### Template 3: Game + Companion Agent

Purpose:

- Test richer state summaries.
- Test recent events.
- Test companion/referee behavior.

AppContext:

- app_type `game`
- assist_mode `companion` or `referee`
- room description
- inventory
- visible options
- recent events

---

### Template 4: Developer Workbench

Purpose:

- Debug context and memory.

Features:

- Chat panel
- App simulation panel
- Context capsule preview
- Retrieved memory preview
- Provider request preview
- Transcript viewer

---

## 9. Configuration Design

### 9.1 Project Config

File: `agentfoundry.yaml`

Example:

```yaml
project:
  id: demo_project
  name: Demo Project

default_provider: mock

providers:
  mock:
    type: mock
    model: mock-model

  ollama_local:
    type: ollama
    base_url: http://localhost:11434
    model: qwen2.5-coder:7b

agent_libraries:
  - ../agents

enabled_agents:
  - chat_companion
  - quiz_tutor
  - game_companion

storage:
  path: .agentfoundry/agent_foundry.sqlite

context_policy:
  include_app_context: true
  max_recent_messages: 12
  app_context_position: before_user_message
```

---

### 9.2 Agent Config

File: `agent.yaml`

Example:

```yaml
id: quiz_tutor
name: Quiz Tutor
version: 0.1.0
description: Gives hints and explanations for quiz questions.
personality_file: personality.md
default_provider: mock
temperature: 0.3

memory:
  enabled: true
  default_scope: session

context_policy:
  include_app_context: true
```

---

## 10. CLI Design

The CLI should help develop and debug the framework.

Commands:

```bash
agentfoundry agents list
agentfoundry agents show AGENT_ID
agentfoundry providers list
agentfoundry providers health
agentfoundry chat AGENT_ID
agentfoundry sessions list
agentfoundry sessions show SESSION_ID
agentfoundry context preview AGENT_ID --message "Hello"
```

All commands should accept:

```bash
--config ./agentfoundry.yaml
```

The CLI should be useful even before any GUI exists.

---

## 11. Milestones

### Milestone 1: Project Skeleton and Agent Loader

Goal:

Create a working Python package that can load reusable agent definitions and personality files.

Deliverables:

- `pyproject.toml`
- package layout
- Pydantic `AgentDefinition`
- `AgentRegistry`
- YAML loading
- personality markdown loading
- sample agents
- CLI commands:
  - `agents list`
  - `agents show`
- tests

Acceptance Criteria:

- `pytest` passes.
- `agentfoundry agents list` shows sample agents.
- `agentfoundry agents show chat_companion` prints agent metadata and personality path.
- Missing files produce clear errors.

---

### Milestone 2: Project Config and Provider Registry

Goal:

Load project configuration and register providers.

Deliverables:

- `ProjectConfig`
- provider config models
- `ProviderRegistry`
- `MockProvider`
- provider health model
- CLI commands:
  - `providers list`
  - `providers health`
- tests

Acceptance Criteria:

- Project config loads from `examples/sample_project/agentfoundry.yaml`.
- Mock provider is available.
- Mock provider health check returns healthy.
- Tests require no network access.

---

### Milestone 3: AppContext and ContextCapsule

Goal:

Create the framework’s context bridge.

Deliverables:

- `AppContext`
- `AssistMode`
- `AllowedKnowledge`
- `ContextPolicy`
- `ContextCapsule`
- markdown renderer for app context
- context manager that assembles basic capsules
- CLI command:
  - `context preview`
- tests

Acceptance Criteria:

- Minimal `AppContext.simple(...)` renders correctly.
- Rich game/quiz contexts render with sections.
- App context appears before the current user message.
- Context preview shows agent personality and app context.

---

### Milestone 4: Runtime Chat with Mock Provider

Goal:

End-to-end chat with an agent using the mock provider.

Deliverables:

- `AgentRuntime`
- `ChatRequest`
- `ChatResponse`
- provider-neutral `Message`
- runtime chat method
- CLI command:
  - `chat AGENT_ID`
- tests

Acceptance Criteria:

- `runtime.chat(...)` returns a deterministic mock response.
- CLI chat works with `chat_companion`.
- Context capsule ID is included in the response.
- No external service is required.

---

### Milestone 5: SQLite Session Memory

Goal:

Persist conversation history.

Deliverables:

- SQLite store
- session creation/loading
- save user and assistant messages
- load recent messages
- session listing
- CLI commands:
  - `sessions list`
  - `sessions show SESSION_ID`
- tests

Acceptance Criteria:

- Chat turns are saved.
- Recent messages are included in later context capsules.
- Sessions are separated by project/agent/user/session IDs.
- Tests use temporary SQLite files.

---

### Milestone 6: Ollama Provider

Goal:

Support local LLMs through Ollama.

Deliverables:

- `OllamaProvider`
- `/api/chat` integration
- health check
- config model
- mocked HTTP tests

Acceptance Criteria:

- Provider formats requests correctly.
- Provider parses responses correctly.
- If Ollama is unavailable, health check reports a clear failure.
- Tests do not require a running Ollama instance.

---

### Milestone 7: OpenAI-Compatible Provider

Goal:

Support OpenAI-compatible HTTP APIs.

Deliverables:

- `OpenAICompatibleProvider`
- `/v1/chat/completions` integration
- API key env var handling
- config model
- mocked HTTP tests

Acceptance Criteria:

- Provider reads API key from configured environment variable.
- Provider formats chat completion requests correctly.
- Missing API key results in a clear error.
- Tests do not call real APIs.

---

### Milestone 8: Example Consumers

Goal:

Show how non-GUI frontend apps would consume the backend.

Deliverables:

- `examples/plain_chatbot.py`
- `examples/quiz_context_demo.py`
- `examples/game_context_demo.py`

Acceptance Criteria:

- Each example can be run with the mock provider.
- Each example demonstrates a different `AppContext` shape.
- Examples are documented in README.

---

## 12. Future Milestones

These are intentionally out of scope for the initial backend.

### Future: NiceGUI Frontend Repo

Use the backend to build:

- Chatbot shell
- Split app + agent shell
- Quiz + hint agent
- Game + companion agent
- Developer workbench

### Future: FastAPI Service

Expose backend over HTTP:

- `GET /agents`
- `POST /agents/{agent_id}/chat`
- `GET /sessions`
- `GET /providers/health`
- `POST /context/preview`

### Future: Memory Providers

Add optional integrations:

- LlamaIndex Memory
- LangGraph checkpointing
- Zep
- Mem0
- pgvector
- Qdrant

### Future: Tool Registry

Allow agents to call project tools:

- read-only SQL
- schema inspector
- repo reader
- test runner
- game action recommender

### Future: Multi-Agent Teams

Support:

- team memory
- coordinator agents
- agent handoff
- shared task state
- per-agent context isolation

---

## 13. Testing Strategy

Use tests to keep the framework stable while features grow.

Test types:

1. Unit tests for Pydantic models.
2. Unit tests for loaders.
3. Unit tests for renderers.
4. Integration tests with mock provider.
5. SQLite tests with temp files.
6. CLI smoke tests.

Do not require:

- Internet
- real OpenAI API calls
- real Ollama server
- GPU
- GUI

---

## 14. Documentation Requirements

README should include:

- What Agent Foundry is
- Installation instructions
- Minimal quickstart
- Config examples
- Agent definition examples
- CLI usage
- Current milestone status
- Known limitations
- Roadmap

Each milestone should update README enough that a developer can test the new functionality.

---

## 15. Initial Quickstart Target

By milestone 4 or 5, this should work:

```bash
agentfoundry --config examples/sample_project/agentfoundry.yaml agents list
agentfoundry --config examples/sample_project/agentfoundry.yaml providers health
agentfoundry --config examples/sample_project/agentfoundry.yaml context preview chat_companion --message "Hello"
agentfoundry --config examples/sample_project/agentfoundry.yaml chat chat_companion
```

And Python usage:

```python
from agent_foundry import AgentRuntime, AppContext

runtime = AgentRuntime.from_project_config("examples/sample_project/agentfoundry.yaml")

response = runtime.chat(
    agent_id="chat_companion",
    project_id="demo_project",
    session_id="demo-session",
    user_id="local-user",
    user_message="Hello there",
    app_context=AppContext.simple(
        app_id="plain_chat",
        app_type="chatbot",
        state_summary="No special app state. This is a plain chatbot session.",
    ),
)

print(response.text)
```

---

## 16. Non-Goals

Agent Foundry backend v0.1 is not:

- A GUI framework
- An autonomous coding agent
- A full LangChain clone
- A vector database
- A hosted service
- A full multi-agent platform
- A security sandbox
- A replacement for application-specific business logic

It is a reusable runtime foundation for app-aware, memory-capable agents.

---

## 17. Success Criteria

This project is successful when a new frontend app can add an agent with minimal code:

```python
response = runtime.chat(
    agent_id="game_companion",
    session_id=current_session,
    user_id=current_user,
    user_message=user_text,
    app_context=current_game_state.to_app_context(),
)
```

The frontend should not manually assemble prompts, manage provider-specific message formats, or decide what memory to retrieve.

Agent Foundry should make the agent feel aware of the app without making the app responsible for the machinery behind the curtain.
