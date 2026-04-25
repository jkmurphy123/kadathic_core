import pytest

from agent_foundry.config.loader import load_project_config
from agent_foundry.core.errors import ConfigurationError
from agent_foundry.providers.mock import MockProvider
from agent_foundry.providers.ollama import OllamaProvider
from agent_foundry.providers.openai_compatible import OpenAICompatibleProvider
from agent_foundry.providers.registry import ProviderRegistry


def test_provider_registry_loads_mock_from_project_config() -> None:
    config = load_project_config("examples/sample_project/agentfoundry.yaml")
    registry = ProviderRegistry.from_project_config(config)

    provider = registry.get("mock")

    assert isinstance(provider, MockProvider)
    assert provider.id == "mock"
    assert registry.ids() == {"mock", "ollama_local", "openai_compatible"}


def test_provider_registry_loads_ollama_from_project_config() -> None:
    config = load_project_config("examples/sample_project/agentfoundry.yaml")
    registry = ProviderRegistry.from_project_config(config)

    provider = registry.get("ollama_local")

    assert isinstance(provider, OllamaProvider)
    assert provider.id == "ollama_local"
    assert provider.base_url == "http://localhost:11434"
    assert provider.model == "qwen2.5-coder:7b-instruct"


def test_provider_registry_loads_openai_compatible_from_project_config() -> None:
    config = load_project_config("examples/sample_project/agentfoundry.yaml")
    registry = ProviderRegistry.from_project_config(config)

    provider = registry.get("openai_compatible")

    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.id == "openai_compatible"
    assert provider.base_url == "https://api.openai.com"
    assert provider.api_key_env == "AGENT_FOUNDRY_OPENAI_COMPATIBLE_KEY"
    assert provider.model == "gpt-4o-mini"


def test_provider_registry_rejects_duplicate_ids() -> None:
    registry = ProviderRegistry()
    registry.register(MockProvider(provider_id="mock"))

    with pytest.raises(ConfigurationError, match="Duplicate provider id"):
        registry.register(MockProvider(provider_id="mock"))


def test_provider_registry_raises_for_unknown_provider() -> None:
    with pytest.raises(ConfigurationError, match="Provider not found"):
        ProviderRegistry().get("missing")
