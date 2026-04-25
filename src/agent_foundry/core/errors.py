"""Framework-specific exceptions."""


class AgentFoundryError(Exception):
    """Base exception for Agent Foundry errors."""


class AgentLoaderError(AgentFoundryError):
    """Raised when an agent definition or personality cannot be loaded."""


class AgentNotFoundError(AgentFoundryError):
    """Raised when an agent id is not registered."""


class ConfigurationError(AgentFoundryError):
    """Raised when lightweight project configuration cannot be loaded."""
