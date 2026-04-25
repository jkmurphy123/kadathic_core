"""Provider registry and construction from project configuration."""

from collections.abc import Iterable

from agent_foundry.config.models import ProjectConfig, ProviderConfig
from agent_foundry.core.errors import ConfigurationError
from agent_foundry.providers.base import ProviderAdapter
from agent_foundry.providers.mock import MockProvider
from agent_foundry.providers.ollama import OllamaProvider


class ProviderRegistry:
    """Stores provider adapters by id."""

    def __init__(self, providers: Iterable[ProviderAdapter] | None = None) -> None:
        self._providers: dict[str, ProviderAdapter] = {}
        for provider in providers or []:
            self.register(provider)

    @classmethod
    def from_project_config(cls, config: ProjectConfig) -> "ProviderRegistry":
        """Build provider adapters from a project config."""

        registry = cls()
        for provider_id, provider_config in config.providers.items():
            registry.register(build_provider(provider_id, provider_config))
        return registry

    def register(self, provider: ProviderAdapter) -> None:
        """Register a provider adapter."""

        if provider.id in self._providers:
            raise ConfigurationError(f"Duplicate provider id: {provider.id}")
        self._providers[provider.id] = provider

    def get(self, provider_id: str) -> ProviderAdapter:
        """Return a provider adapter by id."""

        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise ConfigurationError(f"Provider not found: {provider_id}") from exc

    def list(self) -> list[ProviderAdapter]:
        """Return providers sorted by id."""

        return [self._providers[key] for key in sorted(self._providers)]

    def ids(self) -> set[str]:
        """Return registered provider ids."""

        return set(self._providers)


def build_provider(provider_id: str, config: ProviderConfig) -> ProviderAdapter:
    """Construct a provider adapter from configuration."""

    if config.type == "mock":
        return MockProvider(provider_id=provider_id, model=config.model or "mock-model")
    if config.type == "ollama":
        if not config.model:
            raise ConfigurationError(f"Ollama provider '{provider_id}' requires a model.")
        return OllamaProvider(
            provider_id=provider_id,
            base_url=config.base_url or "http://localhost:11434",
            model=config.model,
        )

    raise ConfigurationError(f"Unsupported provider type: {config.type}")
