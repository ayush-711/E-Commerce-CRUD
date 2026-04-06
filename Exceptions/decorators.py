"""
Custom Exception Handling Decorators
Apply these decorators to route handlers for granular error handling
"""

import logging
from functools import wraps
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ===================== Error Message Mapping (Key-Value Pairs) =====================

ERROR_MESSAGES = {
    # General Errors
    "invalid_value": "Invalid value provided",
    "missing_field": "Missing required field",
    "server_error": "Internal server error",
    "unexpected_error": "An unexpected error occurred",
    
    # Auth Errors
    "auth_failed": "Authentication failed",
    "invalid_credentials": "Invalid email or password",
    "token_expired": "Token has expired",
    "invalid_token": "Invalid token provided",
    "unauthorized": "You are not authenticated",
    
    # Permission Errors
    "access_denied": "Access denied",
    "insufficient_permissions": "You don't have permission to perform this action",
    "admin_only": "This action is restricted to administrators only",
    
    # Database Errors
    "db_error": "Database service temporarily unavailable",
    "db_connection_failed": "Failed to connect to database",
    "user_not_found": "User not found",
    "product_not_found": "Product not found",
    "resource_not_found": "Resource not found",
    
    # Validation Errors
    "type_error": "Invalid data type",
    "validation_error": "Data validation failed",
    "invalid_data": "Invalid data provided",
    
    # Business Logic Errors
    "email_exists": "Email already registered",
    "duplicate_entry": "This entry already exists",
    "invalid_operation": "This operation cannot be performed",
}

# ===================== Helper Function to Get Error Message =====================

def get_error_message(key: str, fallback: str = None) -> str:
    """
    Get error message by key from ERROR_MESSAGES dictionary.
    Args:
        key: Message key to look up
        fallback: Fallback message if key not found
    Returns:
        Error message string
    """
    return ERROR_MESSAGES.get(key, fallback or ERROR_MESSAGES["server_error"])

# ===================== Generic Exception Handler Decorator =====================

def handle_exceptions(func):
    """
    Generic decorator to catch and handle all exceptions in a route handler.
    Wraps the route with try-except and returns formatted error response.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            # HTTPException already has proper formatting, re-raise it
            raise e
        except ValueError as e:
            logger.warning(f"ValueError in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_error_message("invalid_value", str(e))
            )
        except KeyError as e:
            logger.warning(f"KeyError in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_error_message("missing_field", str(e))
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_error_message("server_error")
            )
    
    return wrapper

# ===================== Auth-Specific Decorator =====================

def handle_auth_exceptions(func):
    """
    Decorator for authentication-related endpoints.
    Handles auth-specific exceptions using message mapping.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            raise e
        except ValueError as e:
            logger.warning(f"Auth error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=get_error_message("auth_failed")
            )
        except Exception as e:
            logger.error(f"Auth exception in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_error_message("server_error")
            )
    
    return wrapper

# ===================== Database Operation Decorator =====================

def handle_db_exceptions(func):
    """
    Decorator for database operations.
    Handles DB-specific exceptions using message mapping.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=get_error_message("db_error")
            )
    
    return wrapper

# ===================== Admin-Only Decorator (Combines Auth + RBAC) =====================

def handle_admin_exceptions(func):
    """
    Decorator for admin-only endpoints.
    Checks authorization and handles admin-specific exceptions using message mapping.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            if e.status_code == status.HTTP_403_FORBIDDEN:
                logger.warning(f"Unauthorized admin access attempt: {func.__name__}")
            raise e
        except PermissionError as e:
            logger.warning(f"Permission denied in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=get_error_message("insufficient_permissions")
            )
        except Exception as e:
            logger.error(f"Admin operation error in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_error_message("server_error")
            )
    
    return wrapper

# ===================== Validation Decorator =====================

def handle_validation_exceptions(func):
    """
    Decorator for endpoints with input validation.
    Handles validation-specific exceptions using message mapping.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            raise e
        except TypeError as e:
            logger.warning(f"Type validation error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=get_error_message("type_error")
            )
        except ValueError as e:
            logger.warning(f"Value validation error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=get_error_message("validation_error")
            )
        except Exception as e:
            logger.error(f"Validation error in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_error_message("server_error")
            )
    
    return wrapper

# ===================== Composite Decorator (Multiple Error Types) =====================

def handle_all_exceptions(func):
    """
    Decorator that handles all exception types comprehensively using message mapping.
    Best for general-purpose endpoints.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            raise e
        except ValueError as e:
            logger.warning(f"ValueError in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_error_message("invalid_value", str(e))
            )
        except KeyError as e:
            logger.warning(f"KeyError in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_error_message("missing_field", str(e))
            )
        except TypeError as e:
            logger.warning(f"TypeError in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=get_error_message("type_error")
            )
        except PermissionError as e:
            logger.warning(f"PermissionError in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=get_error_message("access_denied")
            )
        except Exception as e:
            logger.error(f"Unhandled exception in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_error_message("server_error")
            )
    
    return wrapper
