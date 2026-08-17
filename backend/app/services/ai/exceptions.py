class AIGenerationError(Exception):
    """Base exception for all AI layer errors."""
    pass

class GeminiAPIError(AIGenerationError):
    """Raised when the Gemini API returns an error or fails network communication."""
    pass

class ResponseValidationError(AIGenerationError):
    """Raised when generated AI output fails Pydantic schema validation."""
    pass

class ContextBudgetExceededError(AIGenerationError):
    """Raised when supplied or retrieved context exceeds the configured token/character ceiling."""
    pass

class RateLimitExceededError(AIGenerationError):
    """Raised when a user exceeds their permitted generation rate limit."""
    pass
