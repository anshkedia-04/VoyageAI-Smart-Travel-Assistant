class VoyageAIException(Exception):
    """Base application exception for VoyageAI services."""


class ConfigurationError(VoyageAIException):
    """Raised when required configuration or API credentials are missing or invalid."""


class ExternalServiceError(VoyageAIException):
    """Raised when an upstream travel or LLM API fails."""
