from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Callable, Any
from functools import wraps
from ..exceptions import (
    ValidationError,
    AuthenticationError, 
    PermissionError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError
)
from ..logging_config import logger

class BaseRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception_handlers = {
            RequestValidationError: self.handle_validation_error,
            AuthenticationError: self.handle_auth_error,
            PermissionError: self.handle_permission_error,
            NotFoundError: self.handle_not_found_error,
            RateLimitError: self.handle_rate_limit_error,
            ServiceUnavailableError: self.handle_service_error,
            Exception: self.handle_unexpected_error
        }

    def handle_validation_error(self, request: Request, exc: ValidationError):
        logger.warning(f"Validation error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(exc)}
        )

    def handle_auth_error(self, request: Request, exc: AuthenticationError):
        logger.warning(f"Authentication error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": str(exc)}
        )

    def handle_permission_error(self, request: Request, exc: PermissionError):
        logger.warning(f"Permission error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": str(exc)}
        )

    def handle_not_found_error(self, request: Request, exc: NotFoundError):
        logger.warning(f"Not found error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc)}
        )

    def handle_rate_limit_error(self, request: Request, exc: RateLimitError):
        logger.warning(f"Rate limit error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"message": str(exc)}
        )

    def handle_service_error(self, request: Request, exc: ServiceUnavailableError):
        logger.error(f"Service error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"message": str(exc)}
        )

    def handle_unexpected_error(self, request: Request, exc: Exception):
        logger.error(f"Unexpected error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An unexpected error occurred"}
        )

    def route(self, *args, **kwargs):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    raise exc
            return wrapper
        return decorator
