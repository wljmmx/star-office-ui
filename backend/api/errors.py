"""Unified error handling for Star Office UI API."""

import logging
import traceback
from http import HTTPStatus
from typing import Any, Dict, Optional

from flask import jsonify, request
from werkzeug.exceptions import HTTPException

# Configure logger for error handling
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error class."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "API_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        internal_details: Optional[str] = None
    ):
        """
        Initialize API error.
        
        Args:
            message: User-friendly error message
            error_code: Machine-readable error code
            status_code: HTTP status code
            details: Additional error details (safe for clients)
            internal_details: Internal debugging details (never exposed to clients)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.internal_details = internal_details


class ValidationError(APIError):
    """Validation error for invalid input."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details={"field": field, **details} if details else {"field": field}
        )


class NotFoundError(APIError):
    """Resource not found error."""
    
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} '{resource_id}' not found"
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "resource_id": resource_id}
        )


class UnauthorizedError(APIError):
    """Unauthorized access error."""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401
        )


class ForbiddenError(APIError):
    """Forbidden access error."""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=403
        )


class ConflictError(APIError):
    """Resource conflict error."""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409
        )


class InternalServerError(APIError):
    """Internal server error."""
    
    def __init__(
        self,
        message: str = "Internal server error",
        internal_details: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code="INTERNAL_ERROR",
            status_code=500,
            internal_details=internal_details
        )


def make_response(error: APIError, include_details: bool = False) -> tuple:
    """
    Create a standardized error response.
    
    Args:
        error: The API error instance
        include_details: Whether to include safe details in response
        
    Returns:
        Tuple of (response_dict, status_code, headers)
    """
    response = {
        "error": {
            "code": error.error_code,
            "message": error.message
        }
    }
    
    if include_details and error.details:
        response["error"]["details"] = error.details
    
    return response, error.status_code, {"Content-Type": "application/json"}


def log_error(error: Exception, request_info: Optional[Dict[str, Any]] = None):
    """
    Log error with appropriate level and details.
    
    Args:
        error: The exception to log
        request_info: Optional request context information
    """
    # Get request context
    path = request_info.get("path", request.path) if request_info else request.path
    method = request_info.get("method", request.method) if request_info else request.method
    
    # Determine log level based on error type
    if isinstance(error, APIError):
        if error.status_code >= 500:
            level = logging.ERROR
            log_message = f"Internal error: {error.error_code}"
        elif error.status_code >= 400:
            level = logging.WARNING
            log_message = f"Client error: {error.error_code}"
        else:
            level = logging.INFO
            log_message = f"API error: {error.error_code}"
    else:
        level = logging.ERROR
        log_message = f"Unhandled exception: {type(error).__name__}"
    
    # Log with stack trace for 5xx errors
    if isinstance(error, APIError) and error.status_code >= 500:
        if error.internal_details:
            logger.log(level, f"{log_message} - {path} {method}", extra={"request_info": request_info})
            logger.error(error.internal_details, exc_info=False)
        else:
            logger.exception(log_message)
    elif not isinstance(error, APIError):
        logger.exception(log_message)
    else:
        logger.log(level, f"{log_message} - {path} {method}")


def handle_api_error(error: APIError) -> tuple:
    """
    Handle APIError exceptions.
    
    Args:
        error: The API error instance
        
    Returns:
        Response tuple
    """
    # Log the error
    log_error(error)
    
    # Create response (don't expose internal details to clients)
    include_details = not isinstance(error, InternalServerError)
    return make_response(error, include_details=include_details)


def handle_http_exception(error: HTTPException) -> tuple:
    """
    Handle Werkzeug HTTP exceptions.
    
    Args:
        error: The HTTP exception
        
    Returns:
        Response tuple
    """
    # Map to API error
    api_error = APIError(
        message=error.description,
        error_code=error.name,
        status_code=error.code
    )
    
    return handle_api_error(api_error)


def handle_unhandled_exception(error: Exception) -> tuple:
    """
    Handle unhandled exceptions.
    
    Args:
        error: The exception
        
    Returns:
        Response tuple
    """
    # Get stack trace for internal logging
    stack_trace = traceback.format_exc()
    
    # Create internal server error
    api_error = InternalServerError(
        message="An unexpected error occurred",
        internal_details=stack_trace
    )
    
    return handle_api_error(api_error)


def error_handler(error: Exception) -> tuple:
    """
    Central error handler for all exceptions.
    
    Args:
        error: The exception
        
    Returns:
        Response tuple
    """
    if isinstance(error, APIError):
        return handle_api_error(error)
    elif isinstance(error, HTTPException):
        return handle_http_exception(error)
    else:
        return handle_unhandled_exception(error)


def register_error_handlers(app):
    """
    Register error handlers with Flask app.
    
    Args:
        app: Flask application instance
    """
    # Register handler for all exceptions
    @app.errorhandler(Exception)
    def handle_exception(error: Exception):
        return jsonify(error_handler(error)[0]), error_handler(error)[1]
    
    # Register handler for specific HTTP errors
    @app.errorhandler(400)
    def handle_bad_request(error):
        return handle_http_exception(error)
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        return handle_http_exception(error)
    
    @app.errorhandler(403)
    def handle_forbidden(error):
        return handle_http_exception(error)
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return handle_http_exception(error)
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return handle_http_exception(error)
    
    @app.errorhandler(422)
    def handle_unprocessable_entity(error):
        return handle_http_exception(error)
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return handle_http_exception(error)
    
    logger.info("Error handlers registered")
