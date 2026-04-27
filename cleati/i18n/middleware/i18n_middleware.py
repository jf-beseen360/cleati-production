"""
I18n Middleware for FastAPI
Handles language selection and provides translation context for all API endpoints.
"""

from fastapi import Request, HTTPException
from typing import Optional, Callable
from functools import wraps
import json


class I18nMiddleware:
    """Middleware for handling language selection in FastAPI."""

    def __init__(self, i18n_service):
        self.i18n = i18n_service

    async def __call__(self, request: Request, call_next):
        """Process request and set language context."""
        # Get language from headers, query params, or body
        language = self._extract_language(request)

        # Set language in i18n service
        if language:
            self.i18n.set_language(language)

        # Store language in request state for later use
        request.state.language = language or self.i18n.current_language
        request.state.i18n = self.i18n

        response = await call_next(request)
        return response

    def _extract_language(self, request: Request) -> Optional[str]:
        """Extract language from request."""
        # Priority: header > query param > accept-language

        # Check X-Language header
        language = request.headers.get('X-Language')
        if language:
            return language

        # Check language query parameter
        language = request.query_params.get('language')
        if language:
            return language

        # Check Accept-Language header
        accept_language = request.headers.get('Accept-Language', '')
        if accept_language:
            # Extract primary language code
            return accept_language.split(',')[0].split('-')[0].lower()

        return None


def translate_response(namespace: str = 'api'):
    """
    Decorator to automatically translate API response messages.

    Usage:
        @translate_response('api')
        async def endpoint(request: Request):
            return {"message": "project_created"}
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            # Call original function
            result = await func(*args, **kwargs) if request else func(*args, **kwargs)

            # If result is dict with 'message' key, translate it
            if isinstance(result, dict) and 'message' in result:
                i18n = getattr(request.state, 'i18n', None) if request else None
                if i18n:
                    message_key = result['message']
                    result['message'] = i18n.translate(message_key, namespace)
                    # Add language info
                    result['language'] = getattr(request.state, 'language', 'en')

            return result

        return wrapper
    return decorator


class I18nAwareException(HTTPException):
    """HTTPException that uses i18n for error messages."""

    def __init__(self, status_code: int, message_key: str,
                 i18n=None, namespace: str = 'api'):
        self.message_key = message_key
        self.i18n = i18n
        self.namespace = namespace

        # Get translated message
        if i18n:
            detail = i18n.translate(message_key, namespace)
        else:
            detail = message_key

        super().__init__(status_code=status_code, detail=detail)


def get_i18n_context(request: Request):
    """
    Get i18n context from request.

    Usage:
        async def endpoint(request: Request):
            i18n = get_i18n_context(request)
            message = i18n.translate('key')
    """
    return getattr(request.state, 'i18n', None)


def translate_for_response(
    request: Request,
    message_key: str,
    namespace: str = 'api',
    params: dict = None
) -> str:
    """
    Convenience function to translate a message for API response.

    Usage:
        async def endpoint(request: Request):
            msg = translate_for_response(request, 'project_created', 'api')
            return {"message": msg}
    """
    i18n = get_i18n_context(request)
    if i18n:
        return i18n.translate(message_key, namespace, params)
    return message_key


def get_request_language(request: Request) -> str:
    """Get language for current request."""
    return getattr(request.state, 'language', 'en')


# Exception handlers for common API errors

def create_i18n_exception_handlers(i18n_service):
    """Create exception handlers that use i18n."""

    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with i18n."""
        i18n = get_i18n_context(request)

        # Check if detail is a translation key
        if i18n and isinstance(exc.detail, str) and exc.detail.startswith('ERROR_'):
            translated_detail = i18n.translate(exc.detail, 'api')
        else:
            translated_detail = exc.detail

        return {
            "status": "error",
            "code": exc.status_code,
            "message": translated_detail,
            "language": get_request_language(request)
        }

    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        i18n = get_i18n_context(request)

        error_message = i18n.translate('server_error', 'api') if i18n else 'Server error'

        return {
            "status": "error",
            "code": 500,
            "message": error_message,
            "language": get_request_language(request)
        }

    return {
        HTTPException: http_exception_handler,
        Exception: general_exception_handler
    }


# Response models with i18n support

class I18nResponse:
    """Base response class with i18n support."""

    def __init__(self, request: Request, data: dict = None):
        self.request = request
        self.i18n = get_i18n_context(request)
        self.language = get_request_language(request)
        self.data = data or {}

    def success(self, message_key: str, namespace: str = 'api', **extra):
        """Return success response."""
        message = (
            self.i18n.translate(message_key, namespace)
            if self.i18n else message_key
        )
        return {
            "status": "success",
            "message": message,
            "language": self.language,
            **self.data,
            **extra
        }

    def error(self, message_key: str, namespace: str = 'api', status_code: int = 400):
        """Return error response."""
        message = (
            self.i18n.translate(message_key, namespace)
            if self.i18n else message_key
        )
        return {
            "status": "error",
            "message": message,
            "code": status_code,
            "language": self.language
        }

    def translate(self, key: str, namespace: str = 'common', params: dict = None):
        """Translate a key."""
        if self.i18n:
            return self.i18n.translate(key, namespace, params)
        return key
