from typing import Type, TypeVar, Any, Dict
from pydantic import BaseModel, ValidationError
from backend.app.services.ai.exceptions import ResponseValidationError
from backend.app.core.logging import logger

T = TypeVar("T", bound=BaseModel)

class ResponseValidator:
    """
    Validates that raw outputs from LLM calls strictly conform to target Pydantic models.
    """

    @staticmethod
    def validate_schema(data: Any, schema_class: Type[T]) -> T:
        if isinstance(data, schema_class):
            return data
            
        if not isinstance(data, dict):
            raise ResponseValidationError(f"Expected dict-like payload, received {type(data)}")

        try:
            validated = schema_class.model_validate(data)
            logger.info(f"Validated response conforming to {schema_class.__name__}.")
            return validated
        except ValidationError as e:
            logger.error(f"Pydantic schema validation error for {schema_class.__name__}: {e}")
            raise ResponseValidationError(f"Response validation error: {str(e)}")

response_validator = ResponseValidator()
