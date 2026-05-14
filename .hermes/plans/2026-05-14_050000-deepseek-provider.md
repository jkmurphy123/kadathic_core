# Plan: Add DeepSeek Provider to Agent Foundry

**Date:** 2026-05-14
**Goal:** Add a first-class `deepseek` provider type so users can write `type: deepseek` in `agentfoundry.yaml` and get sensible DeepSeek defaults instead of manually wiring `openai_compatible` with the DeepSeek endpoint.

---

## 1. Context / Assumptions

- DeepSeek exposes a standard `/v1/chat/completions` endpoint at `https://api.deepseek.com`.
- The existing `OpenAICompatibleProvider` already works with DeepSeek — but it requires the user to know the base URL, model name, and env var name. A dedicated provider removes that friction.
- The user has a DeepSeek API key and wants a provider that "just works" when configured as `type: deepseek`.
- Reference models: `deepseek-chat` (V3), `deepseek-reasoner` (R1).
- The existing pattern: each provider gets its own file in `src/agent_foundry/providers/`, is registered in `registry.py`'s `build_provider()`, listed in `config/models.py`'s `ProviderConfig.type` Literal, and exported from `__init__.py`.

---

## 2. Design Decision: Thin Wrapper vs. Reuse

**Chosen approach: dedicated class with sensible defaults.**

DeepSeek's API is OpenAI-compatible but has provider-specific defaults worth encoding:

| Concern | Generic `openai_compatible` | Dedicated `deepseek` |
|---------|---------------------------|----------------------|
| Base URL | Must be typed manually | Defaults to `https://api.deepseek.com` |
| API key env var | Must be typed manually | Defaults to `DEEPSEEK_API_KEY` |
| Default model | Must be typed manually | Defaults to `deepseek-chat` |
| Health check | Only checks env var presence | Can check env var + optionally ping the models endpoint |
| User experience | 3 config fields to remember | 1 field: `type: deepseek` |

The implementation will reuse `_text_from_chat_completion` from `openai_compatible.py` (extracting it to a shared utility) and keep provider-specific logic isolated.

---

## 3. Files to Create

### 3.1 `src/agent_foundry/providers/deepseek.py` (new)

A dedicated `DeepSeekProvider` class.

```python
class DeepSeekProvider:
    """Provider adapter for the DeepSeek API (OpenAI-compatible)."""

    DEFAULT_BASE_URL = "https://api.deepseek.com"
    DEFAULT_API_KEY_ENV = "DEEPSEEK_API_KEY"
    DEFAULT_MODEL = "deepseek-chat"

    def __init__(self, *, provider_id, base_url=None, api_key_env=None,
                 model=None, timeout=30.0, client=None):
        # base_url defaults to DEFAULT_BASE_URL if None
        # api_key_env defaults to DEFAULT_API_KEY_ENV if None
        # model defaults to DEFAULT_MODEL if None

    def chat(self, request: ProviderChatRequest) -> ProviderChatResponse:
        # Calls POST /v1/chat/completions
        # Reuses text extraction logic from openai_compatible

    def health_check(self) -> ProviderHealth:
        # Checks DEEPSEEK_API_KEY is set
```

Key design points:
- All three config fields (`base_url`, `api_key_env`, `model`) are optional with sensible defaults.
- Chat implementation mirrors `OpenAICompatibleProvider.chat()`.
- Health check mirrors `OpenAICompatibleProvider.health_check()`.
- The `_text_from_chat_completion` helper should be extracted to a shared location (see 4.1 below).

---

## 4. Files to Edit

### 4.1 `src/agent_foundry/providers/openai_compatible.py` (refactor)

Extract `_text_from_chat_completion()` into `src/agent_foundry/providers/_chat_completion.py` (new shared utility) so both `OpenAICompatibleProvider` and `DeepSeekProvider` can import it without a circular dependency. This is a pure refactor — no behavior change, and existing tests for `OpenAICompatibleProvider` must still pass.

### 4.2 `src/agent_foundry/config/models.py` (edit)

Add `"deepseek"` to the `ProviderConfig.type` Literal:

```python
type: Literal["mock", "ollama", "openai_compatible", "deepseek"]
```

No new fields needed — the existing `base_url`, `api_key_env`, and `model` fields cover DeepSeek's needs.

### 4.3 `src/agent_foundry/providers/registry.py` (edit)

Add import and a `type == "deepseek"` branch to `build_provider()`:

```python
if config.type == "deepseek":
    return DeepSeekProvider(
        provider_id=provider_id,
        base_url=config.base_url or DeepSeekProvider.DEFAULT_BASE_URL,
        api_key_env=config.api_key_env or DeepSeekProvider.DEFAULT_API_KEY_ENV,
        model=config.model or DeepSeekProvider.DEFAULT_MODEL,
    )
```

Note: unlike `openai_compatible`, the DeepSeek provider does NOT require `base_url`, `api_key_env`, or `model` in config — they all have defaults.

### 4.4 `src/agent_foundry/providers/__init__.py` (edit)

Add `DeepSeekProvider` import and export.

### 4.5 `examples/sample_project/agentfoundry.yaml` (edit)

Add a `deepseek` provider entry:

```yaml
  deepseek:
    type: deepseek
    model: deepseek-chat
```

(Minimal — `base_url` and `api_key_env` are omitted since the defaults are correct.)

### 4.6 `README.md` (edit)

Add a "DeepSeek Provider" section between Ollama and OpenAI-Compatible sections (or after OpenAI-Compatible). Document:
- Default endpoints and env vars
- How to configure with `agentfoundry.yaml`
- How to set `DEEPSEEK_API_KEY`
- `providers health` and `providers smoke` usage

---

## 5. Tests to Create

### 5.1 `tests/test_deepseek_provider.py` (new)

Mirror `tests/test_openai_compatible_provider.py`. Tests:

| Test | What it verifies |
|------|-----------------|
| `test_deepseek_provider_formats_request_and_parses_response` | Chat request has correct JSON payload (model, messages, temperature), auth header is `Bearer <key>`, response text/usage/metadata parsed correctly |
| `test_deepseek_provider_uses_defaults_when_not_configured` | When `base_url`, `api_key_env`, `model` are all omitted from constructor, the class defaults to `https://api.deepseek.com`, `DEEPSEEK_API_KEY`, `deepseek-chat` |
| `test_deepseek_provider_missing_api_key` | When `DEEPSEEK_API_KEY` is not set, `chat()` raises `ConfigurationError` with a clear message |
| `test_deepseek_health_check_reports_missing_api_key` | Health check returns `healthy=False` when env var missing |
| `test_deepseek_health_check_reports_configured_api_key` | Health check returns `healthy=True` when env var present |

All tests use `httpx.MockTransport` — no network calls.

### 5.2 `tests/test_provider_registry.py` (edit)

Add one test:

| Test | What it verifies |
|------|-----------------|
| `test_provider_registry_loads_deepseek_from_project_config` | After adding `deepseek` to sample config, registry loads a `DeepSeekProvider` instance with correct defaults |

### 5.3 `tests/test_cli_providers.py` (edit)

Add assertions to existing tests:

- `test_providers_list_sample_project`: assert `"deepseek"` appears in stdout
- `test_providers_health_sample_project`: assert `"deepseek"` appears in stdout, and when `DEEPSEEK_API_KEY` is unset, expect "Set environment variable DEEPSEEK_API_KEY" in output

---

## 6. Acceptance Criteria

1. **Config works:** Adding `type: deepseek` to `agentfoundry.yaml` with just `model: deepseek-chat` builds a working provider (no `base_url` or `api_key_env` required).
2. **CLI lists it:** `agentfoundry providers list` shows the deepseek provider.
3. **CLI health check:** `agentfoundry providers health` reports healthy when `DEEPSEEK_API_KEY` is set, unhealthy when it's missing.
4. **CLI smoke test:** `agentfoundry providers smoke deepseek --prompt "ping"` returns a real response from the DeepSeek API (manual verification — test suite mocks HTTP).
5. **Chat works:** `runtime.chat(...)` with an agent using `default_provider: deepseek` returns a proper `ChatResponse`.
6. **All 48 existing tests still pass** — the refactor of `_text_from_chat_completion` must be transparent.
7. **New tests pass** — 5+ new unit tests covering request formatting, defaults, error cases, and health checks.
8. **README updated** — new provider documented.

---

## 7. Step-by-Step Execution Order

1. **Refactor first:** Extract `_text_from_chat_completion` to `_chat_completion.py`, update imports in `openai_compatible.py`. Run existing tests — all 48 must pass.
2. **Create `deepseek.py`:** New provider class using the shared helper.
3. **Update `config/models.py`:** Add `"deepseek"` to the Literal.
4. **Update `registry.py`:** Add `build_provider` branch.
5. **Update `__init__.py`:** Export `DeepSeekProvider`.
6. **Write tests:** `test_deepseek_provider.py` + edits to registry and CLI tests.
7. **Run all tests:** Expect 55+ passing, 0 failing.
8. **Update sample config and README.**
9. **Manual smoke test:** Set `DEEPSEEK_API_KEY`, run `agentfoundry providers smoke deepseek --prompt "Say hello"`.

---

## 8. Risks and Open Questions

| Risk | Mitigation |
|------|-----------|
| DeepSeek API changes its base URL | The `base_url` config field allows override; default is just a convenience |
| DeepSeek drops OpenAI-compatible format | Low risk — this is their documented API surface. If it happens, the provider can be updated independently of `OpenAICompatibleProvider` |
| `_text_from_chat_completion` extraction creates import churn | Extract to `providers/_chat_completion.py` (underscore-prefixed = internal). Only two files import it |
| User confusion: "why have both `openai_compatible` and `deepseek`?" | They serve different UX goals. `openai_compatible` is the escape hatch for any arbitrary endpoint. `deepseek` is the "just work" experience for DeepSeek users |

**Open question:** Should `providers health` for DeepSeek do a live API ping (like Ollama does with `/api/tags`) or just check the env var (like `openai_compatible`)? For now, match the `openai_compatible` pattern (env var check only) — a live ping would consume tokens and add latency. The `providers smoke` command already serves the live-verification use case.

---

## 9. Summary

This is a straightforward, low-risk addition. ~1 new file, ~5 files edited, ~6 new tests. The refactor of `_text_from_chat_completion` is the only structural change and is transparent to existing code. Estimated: ~30 minutes of implementation.
