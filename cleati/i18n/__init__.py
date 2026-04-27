"""
CLEATI I18n Package
Comprehensive internationalization and localization support
"""

from .services.i18n_service import I18nService, get_i18n_service, t
from .middleware.i18n_middleware import (
    I18nMiddleware,
    I18nAwareException,
    I18nResponse,
    translate_response,
    get_i18n_context,
    translate_for_response,
    get_request_language,
    create_i18n_exception_handlers
)
from .integrations.reports_i18n import (
    I18nReportsGenerator,
    ReportLocalizationHelper
)

__all__ = [
    # Service
    'I18nService',
    'get_i18n_service',
    't',

    # Middleware
    'I18nMiddleware',
    'I18nAwareException',
    'I18nResponse',
    'translate_response',
    'get_i18n_context',
    'translate_for_response',
    'get_request_language',
    'create_i18n_exception_handlers',

    # Reports
    'I18nReportsGenerator',
    'ReportLocalizationHelper',
]

__version__ = '1.0.0'
