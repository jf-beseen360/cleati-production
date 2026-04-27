"""
CLEATI I18n Service
Comprehensive localization and internationalization service with strict language isolation.
"""

import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path


class I18nService:
    """
    Centralized internationalization service for CLEATI.
    Manages translations, locale-specific formatting, and language switching.
    Ensures strict language isolation - no mixing of languages.
    """

    def __init__(self, i18n_dir: str = None):
        """
        Initialize I18n service.

        Args:
            i18n_dir: Root directory containing i18n configuration and translations
        """
        if i18n_dir is None:
            # Default to script location
            i18n_dir = os.path.join(os.path.dirname(__file__), '..')

        self.i18n_dir = i18n_dir
        self.config_path = os.path.join(i18n_dir, 'config.json')
        self.translations_dir = os.path.join(i18n_dir, 'translations')

        # Load configuration
        self.config = self._load_config()
        self.current_language = self.config.get('defaultLanguage', 'en')

        # Load all translations
        self.translations = self._load_all_translations()

    def _load_config(self) -> Dict[str, Any]:
        """Load i18n configuration."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config not found at {self.config_path}")

    def _load_all_translations(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Load all translation files for all languages.

        Returns:
            Dict with structure: {language: {namespace: {key: value}}}
        """
        translations = {}
        languages = self.config.get('languages', {})
        namespaces = self.config.get('supportedNamespaces', [])

        for lang_code in languages.keys():
            translations[lang_code] = {}
            lang_dir = os.path.join(self.translations_dir, lang_code)

            for namespace in namespaces:
                namespace_file = os.path.join(lang_dir, f'{namespace}.json')
                try:
                    with open(namespace_file, 'r', encoding='utf-8') as f:
                        translations[lang_code][namespace] = json.load(f)
                except FileNotFoundError:
                    translations[lang_code][namespace] = {}

        return translations

    def set_language(self, language_code: str) -> bool:
        """
        Switch current language.

        Args:
            language_code: Language code (e.g., 'fr', 'en', 'es')

        Returns:
            True if language set successfully, False if not supported
        """
        if language_code not in self.config.get('languages', {}):
            return False
        self.current_language = language_code
        return True

    def translate(
        self,
        key: str,
        namespace: str = 'common',
        params: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None
    ) -> str:
        """
        Translate a key to current (or specified) language.

        Args:
            key: Translation key (e.g., 'app_name')
            namespace: Translation namespace (common, ui, api, reports, formats)
            params: Optional parameters for string interpolation
            language: Optional override language code

        Returns:
            Translated string or key if translation not found
        """
        lang = language or self.current_language

        # Get translation
        try:
            translation = self.translations[lang][namespace][key]
        except KeyError:
            # Fallback to default language
            fallback_lang = self.config.get('fallbackLanguage', 'en')
            try:
                translation = self.translations[fallback_lang][namespace][key]
            except KeyError:
                return key  # Return key if not found anywhere

        # Apply parameter substitution
        if params:
            try:
                translation = translation.format(**params)
            except (KeyError, IndexError):
                pass  # Return original if substitution fails

        return translation

    def get_locale_config(self, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Get locale configuration for current (or specified) language.

        Args:
            language: Optional language code override

        Returns:
            Locale configuration with date/time/currency formats
        """
        lang = language or self.current_language
        return self.config.get('languages', {}).get(lang, {})

    def format_date(
        self,
        date: datetime,
        format_key: str = 'short',
        language: Optional[str] = None
    ) -> str:
        """
        Format date according to locale.

        Args:
            date: Date to format
            format_key: 'short', 'medium', 'long'
            language: Optional language override

        Returns:
            Formatted date string
        """
        lang = language or self.current_language
        locale_config = self.get_locale_config(lang)

        # Map format keys to format strings from formats namespace
        format_map = {
            'short': self.translate(f'date_{format_key}', 'formats', language=lang),
            'medium': self.translate('date_medium', 'formats', language=lang),
            'long': self.translate('date_long', 'formats', language=lang)
        }

        format_string = format_map.get(format_key, '%m/%d/%Y')

        # Simple date formatting (in production, use babel or similar)
        try:
            return date.strftime(self._convert_format_string(format_string))
        except Exception:
            return date.isoformat()

    def format_number(
        self,
        number: float,
        decimals: int = 2,
        language: Optional[str] = None
    ) -> str:
        """
        Format number according to locale.

        Args:
            number: Number to format
            decimals: Number of decimal places
            language: Optional language override

        Returns:
            Formatted number string
        """
        lang = language or self.current_language
        locale_config = self.get_locale_config(lang)

        decimal_sep = locale_config.get('numberSeparator', '.')
        thousands_sep = locale_config.get('thousandsSeparator', ',')

        # Format number
        format_spec = f',.{decimals}f'
        formatted = format(number, format_spec)

        # Replace separators
        formatted = formatted.replace(',', '|TEMP|')  # Temporary placeholder
        formatted = formatted.replace('.', decimal_sep)
        formatted = formatted.replace('|TEMP|', thousands_sep)

        return formatted

    def format_currency(
        self,
        amount: float,
        currency_code: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """
        Format currency according to locale.

        Args:
            amount: Amount to format
            currency_code: Optional override currency code
            language: Optional language override

        Returns:
            Formatted currency string
        """
        lang = language or self.current_language
        locale_config = self.get_locale_config(lang)

        currency_code = currency_code or locale_config.get('currencyCode', 'EUR')
        currency_symbol = locale_config.get('currencySymbol', '€')
        currency_position = locale_config.get('currencyPosition', 'after')

        # Format the amount
        formatted_amount = self.format_number(amount, decimals=2, language=lang)

        # Apply currency position
        if currency_position == 'before':
            return f"{currency_symbol}{formatted_amount}"
        else:
            return f"{formatted_amount} {currency_symbol}"

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of supported languages.

        Returns:
            List of dicts with language info
        """
        languages = self.config.get('languages', {})
        result = []
        for code, config in languages.items():
            result.append({
                'code': code,
                'name': config.get('name', ''),
                'nativeName': config.get('nativeName', ''),
                'locale': config.get('locale', '')
            })
        return result

    def validate_translation_completeness(self) -> Dict[str, List[str]]:
        """
        Validate that all languages have the same translation keys.

        Returns:
            Dict with any missing keys per language
        """
        languages = list(self.translations.keys())
        missing_by_lang = {}

        for namespace in self.config.get('supportedNamespaces', []):
            # Get keys from default language
            default_lang = self.config.get('defaultLanguage', 'en')
            default_keys = set(self.translations.get(default_lang, {}).get(namespace, {}).keys())

            # Check each language
            for lang in languages:
                lang_keys = set(self.translations.get(lang, {}).get(namespace, {}).keys())
                missing = default_keys - lang_keys

                if missing:
                    if lang not in missing_by_lang:
                        missing_by_lang[lang] = []
                    missing_by_lang[lang].extend([f"{namespace}.{key}" for key in missing])

        return missing_by_lang

    def validate_language_isolation(self) -> Dict[str, List[str]]:
        """
        Validate that translations don't contain text from other languages.

        Returns:
            Dict with any potential language mixing issues
        """
        issues = {}

        # This is a simplified check - in production, use more sophisticated methods
        for lang_code, namespaces in self.translations.items():
            for namespace, keys in namespaces.items():
                for key, value in keys.items():
                    if isinstance(value, str):
                        # Check for common patterns that might indicate mixed languages
                        # This is basic - extend based on your specific needs
                        if any(char in value for char in ['é', 'ê', 'ç'] if lang_code != 'fr'):
                            if lang_code not in issues:
                                issues[lang_code] = []
                            issues[lang_code].append(f"{namespace}.{key}")

        return issues

    def _convert_format_string(self, format_str: str) -> str:
        """
        Convert custom format string to strftime format.

        Args:
            format_str: Format string (e.g., 'dd/MM/yyyy')

        Returns:
            strftime format string
        """
        # Simple conversion - extend based on needs
        format_str = format_str.replace('yyyy', '%Y')
        format_str = format_str.replace('MM', '%m')
        format_str = format_str.replace('dd', '%d')
        format_str = format_str.replace('HH', '%H')
        format_str = format_str.replace('mm', '%M')
        format_str = format_str.replace('ss', '%S')
        return format_str


# Singleton instance
_i18n_instance = None


def get_i18n_service(i18n_dir: str = None) -> I18nService:
    """
    Get or create singleton I18n service instance.

    Args:
        i18n_dir: Optional i18n directory path

    Returns:
        I18nService instance
    """
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18nService(i18n_dir)
    return _i18n_instance


def t(
    key: str,
    namespace: str = 'common',
    params: Optional[Dict[str, Any]] = None,
    language: Optional[str] = None
) -> str:
    """
    Shorthand for translating a key.

    Usage:
        t('app_name')
        t('error_message', params={'name': 'John'})
        t('greeting', language='fr')
    """
    return get_i18n_service().translate(key, namespace, params, language)
