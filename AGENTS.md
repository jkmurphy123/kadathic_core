# AGENTS.md

## Project: Agent Foundry Backend

Agent Foundry is a reusable Python framework for defining, loading, running, and managing AI agents across multiple projects. The framework should let application frontends drop in reusable agents with personalities, provider adapters, short-term memory, long-term memory hooks, and optional app/game/task context.

The first consumer frontend will likely be a NiceGUI app, but this repository should focus on the backend framework only.

---

## Primary Goal

Build a Python backend framework that lets a host application do this:

```python
from agent_foundry import AgentRuntime, AppContext

runtime = AgentRuntime.from_project_config("agentfoundry.yaml")

response = runtime.chat(
    agent_id="chat_companion",
    project_id="demo_project",
    session_id="session-001",
    user_id="local-user",
    user_message="What do you think?",
    app_context=AppContext.simple(
        app_id="demo_app",
        app_type="chatbot",
        state_summary="No special app state. This is a plain chatbot session.",
    ),
)

print(response.text)
```

The application should not need to know how prompts are assembled, how memory is loaded, what provider is used, or how sessions are stored.

---

## Design Principles

1. **Keep the framework backend-first.**
   - No GUI code in this repository.
   - NiceGUI or other UIs should consume this framework through Python imports or, later, an HTTP API.

2. **Prefer boring, testable code.**
   - Use clear Pydantic models.
   - Use dependency injection where practical.
   - Avoid clever metaprogramming.
   - Favor explicit interfaces over hidden magic.

3. **Make providers swappable.**
   - The app should not care whether the agent is powered by Ollama, OpenAI-compatible APIs, OpenClaw Gateway, or a mock provider.

4. **Make context inspectable.**
   - Every agent turn should create a `ContextCapsule` that can be logged, tested, previewed, or exported.
   - When an agent behaves strangely, developers should be able to see exactly what context it saw.

5. **Keep memory scoped.**
   - Session memory, project memory, agent memory, team memory, and user memory must not blur together accidentally.
   - Current app context is authoritative over stale memory.

6. **Start simple.**
   - v0.1 should not implement complex RAG, vector memory, multi-agent orchestration, or autonomous planning.
   - Build stable interfaces first, then add integrations behind them.

---

## Preferred Technology Stack

Use:

- Python 3.11+
- Pydantic v2
- Typer for CLI
- Rich for CLI display
- PyYAML or ruamel.yaml for YAML loading
- SQLite for initial session/transcript storage
- httpx for provider HTTP calls
- pytest for tests
- ruff for linting/formatting
- pyproject.toml-based packaging

Avoid unless explicitly requested:

- LangChain/LangGraph as hard dependencies in milestone 1
- LlamaIndex as a hard dependency in milestone 1
- Heavy web frameworks in the core package
- GUI dependencies
- Database servers for the initial version

---

## Repository Layout

Create a repository structure similar to this:

```text
agent-foundry/
  AGENTS.md
  README.md
  pyproject.toml

  src/
    agent_foundry/
      __init__.py

      core/
        runtime.py
        models.py
        errors.py

      agents/
        definition.py
        registry.py
        loader.py

      context/
        app_context.py
        capsule.py
        manager.py
        policy.py
        renderer.py

      providers/
        base.py
        mock.py
        ollama.py
        openai_compatible.py
        registry.py

      memory/
        base.py
        scopes.py
        manager.py
        sqlite_store.py
        null.py

      storage/
        sqlite.py
        sessions.py

      config/
        models.py
        loader.py

      tools/
        base.py
        registry.py

      cli/
        main.py

  examples/
    agents/
      chat_companion/
        agent.yaml
        personality.md

      quiz_tutor/
        agent.yaml
        personality.md

      game_companion/
        agent.yaml
        personality.md

    sample_project/
      agentfoundry.yaml

  tests/
    test_agent_loader.py
    test_context_manager.py
    test_app_context.py
    test_mock_provider.py
    test_runtime_chat.py
    test_sqlite_memory.py
```

The exact layout may evolve, but preserve these conceptual modules.

---

## Public API Targets

The backend should eventually expose these imports:

```python
from agent_foundry import (
    AgentRuntime,
    AppContext,
    ChatRequest,
    ChatResponse,
    AgentDefinition,
)
```

The core runtime call should look like:

```python
response = runtime.chat(
    agent_id="chat_companion",
    project_id="demo_project",
    session_id="session-001",
    user_id="local-user",
    user_message="Hello",
    app_context=None,
)
```

Return a `ChatResponse` with at least:

```python
class ChatResponse(BaseModel):
    text: str
    agent_id: str
    session_id: str
    provider_id: str
    model: str | None = None
    context_capsule_id: str | None = None
    usage: dict = {}
    metadata: dict = {}
```

---

## AppContext Contract

Create a reusable `AppContext` model. It is the bridge between an arbitrary frontend app and the agent context manager.

Minimum model:

```python
from typing import Any, Literal
from pydantic import BaseModel, Field

AssistMode = Literal[
    "companion",
    "hint_giver",
    "tutor",
    "referee",
    "spoiler_allowed",
    "debug",
]

AllowedKnowledge = Literal[
    "player_visible_only",
    "answer_key_allowed",
    "director_notes_allowed",
    "debug_full_state",
]

class AppContext(BaseModel):
    app_id: str
    app_type: str
    title: str | None = None
    assist_mode: AssistMode = "companion"
    allowed_knowledge: AllowedKnowledge = "player_visible_only"

    state_summary: str

    user_goal: str | None = None
    current_task: str | None = None
    visible_options: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    recent_events: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def simple(
        cls,
        app_id: str,
        app_type: str,
        state_summary: str,
        title: str | None = None,
        assist_mode: AssistMode = "companion",
    ) -> "AppContext":
        return cls(
            app_id=app_id,
            app_type=app_type,
            title=title,
            state_summary=state_summary,
            assist_mode=assist_mode,
        )
```

The context renderer should convert `AppContext` into a clear markdown section.

---

## ContextCapsule Contract

Every chat turn should assemble a `ContextCapsule`.

Suggested model:

```python
class ContextCapsule(BaseModel):
    id: str
    user_id: str
    project_id: str
    agent_id: str
    session_id: str

    system_instructions: str
    agent_personality: str
    project_context: str | None = None
    memory_context: str | None = None
    session_summary: str | None = None
    recent_messages: list[Message] = []
    app_context: AppContext | None = None
    current_user_message: str

    rendered_messages: list[Message]
    metadata: dict = {}
```

The provider adapter receives `rendered_messages`, not raw app state.

---

## Context Priority Rules

When assembling context, use this priority order:

1. System/framework safety instructions
2. Agent personality
3. Project rules
4. Current app context
5. Current user message
6. Session history
7. Long-term memory

For factual app/game state, current `AppContext` wins over stale memory or prior conversation.

Example:
If memory says the player had a bronze key but current app context says inventory is empty, the agent should trust current app context.

---

## Provider Adapter Interface

Create a provider abstraction.

```python
class ProviderAdapter(Protocol):
    id: str

    def chat(self, request: ProviderChatRequest) -> ProviderChatResponse:
        ...

    def health_check(self) -> ProviderHealth:
        ...
```

Required providers for early milestones:

1. `MockProvider`
   - Deterministic test provider.
   - Should echo or return predictable responses.
   - Must require no external services.

2. `OllamaProvider`
   - Calls local Ollama `/api/chat`.
   - Configurable `base_url` and `model`.
   - Should have a health check.

3. `OpenAICompatibleProvider`
   - Calls `/v1/chat/completions`.
   - Configurable `base_url`, `api_key_env`, and `model`.
   - Should not hardcode a vendor name into the interface.

Do not expose provider-specific request formats to host applications.

---

## Memory Requirements

Milestone 1 memory should be simple:

- Save transcript messages by `project_id`, `agent_id`, `session_id`, and `user_id`.
- Load recent messages for a session.
- Support no-memory mode for tests.
- Support simple session summaries later.

Define scopes even if not all are fully implemented yet:

```python
MemoryScopeName = Literal[
    "session",
    "agent_project",
    "project",
    "agent_global",
    "user_global",
    "team",
]
```

Memory interfaces should make room for future providers:

- SQLite local memory
- LlamaIndex memory
- Zep
- Mem0
- pgvector/Qdrant/Chroma

But do not implement those advanced providers in the first milestone.

---

## Configuration Files

Support global-ish project config via `agentfoundry.yaml`.

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

Agent definition example:

```yaml
id: chat_companion
name: Chat Companion
version: 0.1.0
description: A simple friendly chatbot agent.
personality_file: personality.md
default_provider: mock
temperature: 0.4

memory:
  enabled: true
  default_scope: session

context_policy:
  include_app_context: false
```

---

## CLI Requirements

Build a Typer CLI called `agentfoundry`.

Minimum commands:

```bash
agentfoundry agents list
agentfoundry agents show chat_companion
agentfoundry providers list
agentfoundry providers health
agentfoundry chat chat_companion
agentfoundry sessions list
agentfoundry sessions show SESSION_ID
agentfoundry context preview chat_companion --message "Hello"
```

All CLI commands should accept a project config path:

```bash
agentfoundry --config ./agentfoundry.yaml agents list
```

Use Rich for readable output.

---

## Testing Requirements

Use pytest.

Write tests for:

- Loading agent definitions from folders.
- Loading personality markdown.
- Handling missing personality files with clear errors.
- Loading project config.
- Rendering minimal `AppContext`.
- Rendering rich `AppContext`.
- Assembling `ContextCapsule`.
- Ensuring current app context appears near the current user message.
- Ensuring mock provider returns deterministic text.
- Saving and loading session messages from SQLite.
- Runtime chat with mock provider.
- CLI smoke tests where practical.

Tests should not require network access, Ollama, OpenAI, or external services.

---

## Coding Style

- Use type hints everywhere.
- Prefer Pydantic models for external/config/API-shaped data.
- Keep functions small.
- Raise framework-specific exceptions from `core/errors.py`.
- No broad `except Exception` unless re-raising with useful context.
- Do not print from core library code.
- CLI may print.
- Avoid global mutable state.
- Write docstrings for public classes and methods.

---

## Milestone Discipline

Implement one milestone at a time.

For each milestone:

1. Update README with the new feature.
2. Add or update tests.
3. Keep the mock provider working.
4. Avoid adding unrelated features.
5. Prefer simple placeholder interfaces over incomplete complex implementations.

---

## Initial Milestones

### Milestone 1: Project Skeleton and Agent Loader

Implement:

- Python package layout
- `pyproject.toml`
- `AgentDefinition`
- `AgentRegistry`
- YAML loader
- personality markdown loader
- sample agents
- CLI: `agents list`, `agents show`
- tests

### Milestone 2: Config and Provider Registry

Implement:

- `ProjectConfig`
- provider config models
- `ProviderRegistry`
- `MockProvider`
- CLI: `providers list`, `providers health`
- tests

### Milestone 3: Context and AppContext

Implement:

- `AppContext`
- `ContextPolicy`
- `ContextCapsule`
- markdown renderer for app context
- context manager with mock data
- CLI: `context preview`
- tests

### Milestone 4: Runtime Chat with Mock Provider

Implement:

- `AgentRuntime`
- `ChatRequest`
- `ChatResponse`
- provider-neutral messages
- prompt assembly
- CLI: `chat`
- tests

### Milestone 5: SQLite Session Memory

Implement:

- SQLite session store
- save user/assistant messages
- load recent messages
- list sessions
- show session
- tests

### Milestone 6: Ollama Provider

Implement:

- Ollama `/api/chat` support
- health check
- graceful failure if Ollama unavailable
- provider config
- tests using mocked HTTP calls

### Milestone 7: OpenAI-Compatible Provider

Implement:

- `/v1/chat/completions` support
- API key env var handling
- mocked HTTP tests
- provider config

### Milestone 8: Example Consumer Apps

Add examples, not GUI yet:

- Plain chatbot example
- Quiz context example
- Game context example

Each example should demonstrate how a frontend would call `runtime.chat(...)`.

---

## Do Not Build Yet

Do not implement in early milestones unless explicitly requested:

- NiceGUI frontend
- React frontend
- FastAPI service
- LangGraph integration
- LlamaIndex integration
- Zep/Mem0 integration
- Vector memory
- Multi-agent orchestration
- Tool execution loops
- Autonomous planning
- File system agent tools
- Shell command tools

Leave clean extension points for these.

---

## Final Reminder

The purpose of this backend is to make frontend apps simple.

A frontend should only need to provide:

1. `agent_id`
2. `user_message`
3. `session_id`
4. optional `AppContext`

Everything else should be handled by Agent Foundry.
