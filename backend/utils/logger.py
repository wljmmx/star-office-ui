"""
Star Office UI - Structured Logging Module

Implements structured logging using structlog with:
- JSON formatting for ELK stack compatibility
- Multiple outputs (console, file)
- Context information injection
- Request/response logging
- Database operation logging
- Error tracking with full stack traces
- Sensitive data filtering
"""

import logging
import sys
import json
import traceback
import os
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps

import structlog
from structlog.processors import JSONRenderer, add_log_level, add_timestamp, StackInfoRenderer
from structlog.stdlib import ProcessorFormatter, add_logger_name, filter_by_level
from structlog.contextvars import merge_contextvars, bound_contextvars

# Sensitive headers to filter out
SENSITIVE_HEADERS = {
    'Authorization',
    'Cookie',
    'Set-Cookie',
    'X-Api-Key',
    'X-Auth-Token',
    'Proxy-Authorization',
    'WWW-Authenticate'
}


# Configure standard logging backend
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.NOTSET
)

# Log level mapping
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


def get_logger(name: str = "star_office") -> structlog.BoundLogger:
    """
    Get a configured structlog logger.
    
    Args:
        name: Logger name (default: "star_office")
    
    Returns:
        Configured structlog BoundLogger instance
    """
    return structlog.get_logger(name)


def configure_structlog(
    log_level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True,
    log_file_path: str = "/var/log/star-office/app.log"
) -> None:
    """
    Configure structlog with processors and formatters.
    
    Args:
        log_level: Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        console_output: Enable console output
        file_output: Enable file output
        log_file_path: Path to log file
    """
    # Processors for structlog
    processors = [
        # Add timestamp in ISO format
        add_timestamp(fmt="%Y-%m-%dT%H:%M:%S.%fZ"),
        # Add log level
        add_log_level(),
        # Add logger name
        add_logger_name(),
        # Merge context variables
        merge_contextvars(),
        # Add stack info for errors
        StackInfoRenderer(),
        # Render as JSON
        JSONRenderer()
    ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVELS.get(log_level.upper(), logging.INFO)),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False
    )
    
    # Setup standard logging handlers
    _setup_handlers(log_level, console_output, file_output, log_file_path)


def _setup_handlers(
    log_level: str,
    console_output: bool,
    file_output: bool,
    log_file_path: str
) -> None:
    """Setup logging handlers for console and file output."""
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with ProcessorFormatter
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
        
        # Use ProcessorFormatter to convert structlog records to standard logging
        processor_formatter = ProcessorFormatter(
            processor=JSONRenderer(),
            foreign_pre_chain=[
                add_log_level(),
                add_timestamp(fmt="%Y-%m-%dT%H:%M:%S.%fZ"),
                add_logger_name(),
            ]
        )
        console_handler.setFormatter(processor_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if file_output:
        from logging.handlers import TimedRotatingFileHandler
        
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # TimedRotatingFileHandler: rotate daily, keep 7 days
        file_handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when="midnight",  # Rotate at midnight
            interval=1,       # Every 1 day
            backupCount=7,    # Keep 7 days of logs
            encoding="utf-8"
        )
        file_handler.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
        
        # Use the same formatter
        processor_formatter = ProcessorFormatter(
            processor=JSONRenderer(),
            foreign_pre_chain=[
                add_log_level(),
                add_timestamp(fmt="%Y-%m-%dT%H:%M:%S.%fZ"),
                add_logger_name(),
            ]
        )
        file_handler.setFormatter(processor_formatter)
        root_logger.addHandler(file_handler)


def filter_sensitive_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Filter out sensitive headers from request headers.
    
    Args:
        headers: Original headers dictionary
    
    Returns:
        Filtered headers with sensitive values masked
    """
    filtered = {}
    for key, value in headers.items():
        if key.lower() in [h.lower() for h in SENSITIVE_HEADERS]:
            # Mask sensitive headers
            if 'authorization' in key.lower():
                filtered[key] = 'REDACTED'
            elif 'cookie' in key.lower():
                filtered[key] = 'REDACTED'
            else:
                filtered[key] = 'REDACTED'
        else:
            filtered[key] = value
    return filtered


class RequestContext:
    """Context manager for request-scoped logging context."""
    
    def __init__(
        self,
        request_id: str,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None
    ):
        self.request_id = request_id
        self.user_id = user_id
        self.endpoint = endpoint
        self.method = method
    
    def __enter__(self):
        """Set context variables for the request."""
        structlog.contextvars.bind_contextvars(
            request_id=self.request_id,
            user_id=self.user_id,
            endpoint=self.endpoint,
            method=self.method
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clear context variables after request."""
        structlog.contextvars.reset_contextvars()


def log_request(func):
    """
    Decorator to log API requests and responses.
    
    Usage:
        @log_request
        def my_endpoint(request):
            return {"status": "success"}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Extract request info
        request = None
        if args:
            request = args[0]
        
        # Generate request ID if not present
        import uuid
        request_id = kwargs.get('request_id') or request.headers.get('X-Request-ID') or str(uuid.uuid4())
        
        # Extract method and endpoint
        method = request.method if request else "UNKNOWN"
        endpoint = request.path if hasattr(request, 'path') else func.__name__
        
        # Filter sensitive headers
        safe_headers = filter_sensitive_headers(dict(request.headers)) if request else {}
        
        # Log request
        logger.info(
            "request_received",
            request_id=request_id,
            method=method,
            endpoint=endpoint,
            headers=safe_headers
        )
        
        # Execute function with timing
        import time
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            elapsed_time = time.time() - start_time
            
            logger.info(
                "request_completed",
                request_id=request_id,
                method=method,
                endpoint=endpoint,
                elapsed_time=elapsed_time,
                status="success"
            )
            
            return result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            
            logger.error(
                "request_failed",
                request_id=request_id,
                method=method,
                endpoint=endpoint,
                elapsed_time=elapsed_time,
                error=str(e),
                stack_info=True
            )
            
            raise
    
    return wrapper


def log_database_operation(operation: str, table: str = None):
    """
    Decorator to log database operations.
    
    Usage:
        @log_database_operation("SELECT", "users")
        def get_users():
            return User.query.all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            
            logger.info(
                "database_operation_start",
                operation=operation,
                table=table,
                function=func.__name__
            )
            
            try:
                result = func(*args, **kwargs)
                
                logger.info(
                    "database_operation_success",
                    operation=operation,
                    table=table,
                    function=func.__name__
                )
                
                return result
                
            except Exception as e:
                logger.error(
                    "database_operation_failed",
                    operation=operation,
                    table=table,
                    function=func.__name__,
                    error=str(e),
                    stack_info=True
                )
                raise
        
        return wrapper
    return decorator


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """
    Log an error with full stack trace.
    
    Args:
        error: Exception instance
        context: Additional context information
    """
    logger = get_logger("star_office.errors")
    
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "stack_trace": traceback.format_exc(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if context:
        log_data.update(context)
    
    logger.error("unhandled_error", **log_data)


def add_context(**kwargs):
    """
    Add context variables to all log messages in the current scope.
    
    Usage:
        with add_context(user_id=123, action="update_profile"):
            logger.info("processing request")
    """
    return bound_contextvars(**kwargs)


# Pre-configured logger instances for common use cases
api_logger = None
db_logger = None
error_logger = None


def get_api_logger() -> structlog.BoundLogger:
    """Get logger for API requests."""
    global api_logger
    if api_logger is None:
        api_logger = get_logger("star_office.api")
    return api_logger


def get_db_logger() -> structlog.BoundLogger:
    """Get logger for database operations."""
    global db_logger
    if db_logger is None:
        db_logger = get_logger("star_office.database")
    return db_logger


def get_error_logger() -> structlog.BoundLogger:
    """Get logger for error tracking."""
    global error_logger
    if error_logger is None:
        error_logger = get_logger("star_office.errors")
    return error_logger
