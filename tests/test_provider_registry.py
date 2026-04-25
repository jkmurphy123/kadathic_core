import pytest

from agent_foundry.config.loader import load_project_config
from agent_foundry.core.errors import ConfigurationError
from agent_foundry.providers.mock import MockProvider
from agent_foundry.providers.registry import ProviderRegistry


def test_provider_registry_loads_mock_from_project_config() -> None:
    config = load_project_config("examples/sample_project/agentfoundry.yaml")
    registry = ProviderRegistry.from_project_config(config)

    provider = registry.get("mock")

    assert isinstance(provider, MockProvider)
    assert provider.id == "mock"
    assert registry.ids() == {"mock"}


def test_provider_registry_rejects_duplicate_ids() -> None:
    registry = ProviderRegistry()
    registry.register(MockProvider(provider_id="mock"))

    with pytest.raises(ConfigurationError, match="Duplicate provider id"):
        registry.register(MockProvider(provider_id="mock"))


def test_provider_registry_raises_for_unknown_provider() -> None:
    with pytest.raises(ConfigurationError, match="Provider not found"):
        ProviderRegistry().get("missing")
