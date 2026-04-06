from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI):
    """
    Register all global exception handlers for the FastAPI application
    """
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        Handles all unhandled exceptions globally
        Logs the error and returns a consistent error response
        """
        logger.error(f"Unhandled Exception on {request.url.path}: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "type": type(exc).__name__,
                "message": str(exc)
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handles Pydantic validation errors with detailed feedback
        """
        logger.warning(f"Validation Error on {request.url.path}: {exc.errors()}")
        
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": exc.errors()
            }
        )
