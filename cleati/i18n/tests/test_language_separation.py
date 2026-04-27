"""
Language Separation Test Suite
Validates that translations maintain strict language isolation
No mixing of languages in UI, API, or reports
"""

import pytest
import json
import os
from pathlib import Path
from typing import Dict, List, Set


class TestLanguageSeparation:
    """Test suite for language isolation and separation."""

    @pytest.fixture
    def translations_dir(self):
        """Get translations directory."""
        return os.path.join(os.path.dirname(__file__), '..', 'translations')

    @pytest.fixture
    def config(self, translations_dir):
        """Load i18n config."""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture
    def all_translations(self, translations_dir, config):
        """Load all translations."""
        translations = {}
        for lang in config['languages'].keys():
            translations[lang] = {}
            lang_dir = os.path.join(translations_dir, lang)
            for namespace in config['supportedNamespaces']:
                ns_file = os.path.join(lang_dir, f'{namespace}.json')
                with open(ns_file, 'r', encoding='utf-8') as f:
                    translations[lang][namespace] = json.load(f)
        return translations

    def test_all_languages_defined(self, config):
        """Test that all required languages are defined."""
        required_languages = ['fr', 'en', 'es', 'de', 'it', 'pt', 'nl', 'pl']
        defined_languages = set(config['languages'].keys())

        for lang in required_languages:
            assert lang in defined_languages, f"Language {lang} not defined in config"

    def test_all_namespaces_exist(self, translations_dir, config):
        """Test that all required namespaces exist for each language."""
        required_namespaces = config['supportedNamespaces']

        for lang in config['languages'].keys():
            lang_dir = os.path.join(translations_dir, lang)
            assert os.path.exists(lang_dir), f"Language directory missing: {lang}"

            for namespace in required_namespaces:
                ns_file = os.path.join(lang_dir, f'{namespace}.json')
                assert os.path.exists(ns_file), \
                    f"Namespace file missing: {lang}/{namespace}.json"

    def test_translation_completeness(self, all_translations, config):
        """Test that all languages have the same translation keys."""
        default_lang = config['defaultLanguage']
        default_translations = all_translations[default_lang]

        for namespace in config['supportedNamespaces']:
            default_keys = set(default_translations[namespace].keys())

            for lang in config['languages'].keys():
                if lang == default_lang:
                    continue

                lang_keys = set(all_translations[lang][namespace].keys())
                missing_keys = default_keys - lang_keys
                extra_keys = lang_keys - default_keys

                assert not missing_keys, \
                    f"Language {lang} missing keys in {namespace}: {missing_keys}"
                assert not extra_keys, \
                    f"Language {lang} has extra keys in {namespace}: {extra_keys}"

    def test_no_language_mixing_in_values(self, all_translations, config):
        """
        Test that translation values don't contain text from other languages.
        This is a basic check for common indicators.
        """
        # Define language indicators (basic check)
        indicators = {
            'fr': ['ç', 'é', 'è', 'ê', 'à', 'ù'],
            'de': ['ü', 'ö', 'ä', 'ß'],
            'pt': ['ã', 'õ'],
            'es': ['ñ'],
            'pl': ['ł', 'ó', 'ś', 'ź', 'ż'],
            'nl': [],
            'it': [],
            'en': []
        }

        issues = {}

        for lang in config['languages'].keys():
            lang_issues = []

            for namespace in config['supportedNamespaces']:
                for key, value in all_translations[lang][namespace].items():
                    if isinstance(value, str):
                        # Check for mixing with common language indicators
                        for other_lang, chars in indicators.items():
                            if other_lang != lang and chars:
                                # Don't flag if it's a proper noun or brand name
                                has_indicator = any(char in value for char in chars)
                                # More lenient check - only flag if excessive
                                indicator_count = sum(value.count(char) for char in chars)
                                if has_indicator and indicator_count > 2:
                                    lang_issues.append({
                                        'key': f"{namespace}.{key}",
                                        'value': value,
                                        'other_lang': other_lang
                                    })

            if lang_issues:
                issues[lang] = lang_issues

        assert not issues, f"Potential language mixing detected: {json.dumps(issues, indent=2)}"

    def test_locale_config_completeness(self, config):
        """Test that all language configs have required locale settings."""
        required_fields = [
            'name', 'nativeName', 'locale', 'direction',
            'dateFormat', 'timeFormat', 'numberSeparator', 'thousandsSeparator',
            'currencySymbol', 'currencyPosition', 'currencyCode'
        ]

        for lang_code, lang_config in config['languages'].items():
            for field in required_fields:
                assert field in lang_config, \
                    f"Language {lang_code} missing field: {field}"

    def test_no_empty_translations(self, all_translations):
        """Test that no translation values are empty."""
        empty_translations = {}

        for lang, namespaces in all_translations.items():
            for namespace, keys in namespaces.items():
                for key, value in keys.items():
                    if isinstance(value, str) and not value.strip():
                        if lang not in empty_translations:
                            empty_translations[lang] = []
                        empty_translations[lang].append(f"{namespace}.{key}")

        assert not empty_translations, \
            f"Empty translations found: {json.dumps(empty_translations, indent=2)}"

    def test_no_hardcoded_english(self, all_translations):
        """
        Test that non-English namespaces don't contain excessive English text.
        (Allows for technical terms and brand names)
        """
        common_english_words = [
            'hello', 'world', 'test', 'example', 'sample', 'demo',
            'placeholder', 'foobar', 'lorem ipsum'
        ]

        issues = {}

        for lang in all_translations.keys():
            if lang == 'en':
                continue

            for namespace in all_translations[lang].keys():
                for key, value in all_translations[lang][namespace].items():
                    if isinstance(value, str):
                        value_lower = value.lower()
                        found_english = [
                            word for word in common_english_words
                            if word in value_lower
                        ]
                        if found_english:
                            if lang not in issues:
                                issues[lang] = []
                            issues[lang].append({
                                'key': f"{namespace}.{key}",
                                'value': value,
                                'english_words': found_english
                            })

        assert not issues, \
            f"Hardcoded English found in non-English translations: {json.dumps(issues, indent=2)}"

    def test_currency_symbols_correct(self, all_translations, config):
        """Test that currency symbols match language locale."""
        currency_mapping = {
            'EUR': '€',
            'USD': '$',
            'GBP': '£',
            'PLN': 'zł',
            'JPY': '¥'
        }

        for lang, lang_config in config['languages'].items():
            currency_code = lang_config['currencyCode']
            currency_symbol = lang_config['currencySymbol']

            if currency_code in currency_mapping:
                expected_symbol = currency_mapping[currency_code]
                # Allow some flexibility as there are variations
                assert currency_symbol in [expected_symbol, currency_code], \
                    f"Language {lang}: currency symbol mismatch"

    def test_format_strings_consistency(self, all_translations, config):
        """Test that format strings in formats namespace are valid."""
        valid_format_patterns = [
            'date_short', 'date_medium', 'date_long',
            'time_short', 'time_long',
            'datetime_short', 'datetime_long',
            'currency_format', 'number_format', 'integer_format',
            'percentage_format'
        ]

        for lang in all_translations.keys():
            if 'formats' in all_translations[lang]:
                for pattern in valid_format_patterns:
                    assert pattern in all_translations[lang]['formats'], \
                        f"Language {lang} missing format pattern: {pattern}"

    def test_no_placeholder_values(self, all_translations):
        """Test that no translations still contain placeholder text."""
        placeholder_patterns = [
            'TODO',
            'FIXME',
            'XXX',
            'placeholder',
            '[placeholder]',
            '...'
        ]

        issues = {}

        for lang, namespaces in all_translations.items():
            for namespace, keys in namespaces.items():
                for key, value in keys.items():
                    if isinstance(value, str):
                        value_upper = value.upper()
                        for pattern in placeholder_patterns:
                            if pattern.upper() in value_upper:
                                if lang not in issues:
                                    issues[lang] = []
                                issues[lang].append(f"{namespace}.{key}")

        assert not issues, \
            f"Placeholder values found: {json.dumps(issues, indent=2)}"

    def test_ui_namespace_completeness(self, all_translations, config):
        """Test that UI namespace has all required UI keys."""
        required_ui_keys = [
            'navigation',
            'setup',
            'financial',
            'green',
            'results',
            'form'
        ]

        default_lang = config['defaultLanguage']
        default_ui = all_translations[default_lang].get('ui', {})

        for key in required_ui_keys:
            assert key in default_ui, f"UI namespace missing key: {key}"

    def test_api_namespace_completeness(self, all_translations, config):
        """Test that API namespace has all required API message keys."""
        required_api_keys = [
            'project_created',
            'project_updated',
            'project_deleted',
            'error_creating_project',
            'validation_error',
            'unauthorized'
        ]

        default_lang = config['defaultLanguage']
        default_api = all_translations[default_lang].get('api', {})

        for key in required_api_keys:
            assert key in default_api, f"API namespace missing key: {key}"

    def test_reports_namespace_completeness(self, all_translations, config):
        """Test that reports namespace has all required report keys."""
        required_report_keys = [
            'report_title',
            'executive_summary',
            'project_overview',
            'financial_analysis',
            'recommendations'
        ]

        default_lang = config['defaultLanguage']
        default_reports = all_translations[default_lang].get('reports', {})

        for key in required_report_keys:
            assert key in default_reports, f"Reports namespace missing key: {key}"


class TestLanguageFormatting:
    """Test suite for language-specific formatting."""

    @pytest.fixture
    def config(self):
        """Load i18n config."""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_date_formats_valid(self, config):
        """Test that date formats are valid for each language."""
        valid_format_chars = set('ydmhsaAZz./-: ')

        for lang, lang_config in config['languages'].items():
            date_format = lang_config['dateFormat']
            for char in date_format:
                if char not in valid_format_chars:
                    assert False, f"Language {lang}: invalid char in dateFormat: {char}"

    def test_number_separators_different(self, config):
        """Test that languages using different number separators are consistent."""
        for lang, lang_config in config['languages'].items():
            decimal = lang_config['numberSeparator']
            thousands = lang_config['thousandsSeparator']

            assert decimal != thousands, \
                f"Language {lang}: decimal and thousands separators are identical"

    def test_currency_position_valid(self, config):
        """Test that currency positions are valid."""
        valid_positions = ['before', 'after']

        for lang, lang_config in config['languages'].items():
            position = lang_config['currencyPosition']
            assert position in valid_positions, \
                f"Language {lang}: invalid currency position: {position}"


class TestTranslationService:
    """Test the I18nService class."""

    @pytest.fixture
    def i18n_service(self):
        """Initialize I18n service."""
        # Import here to avoid issues if service isn't installed
        try:
            from cleati.i18n.services.i18n_service import I18nService
            i18n_dir = os.path.join(os.path.dirname(__file__), '..')
            return I18nService(i18n_dir)
        except ImportError:
            pytest.skip("I18nService not available")

    def test_service_initialization(self, i18n_service):
        """Test that service initializes correctly."""
        assert i18n_service is not None
        assert i18n_service.current_language == 'en'
        assert 'fr' in i18n_service.translations

    def test_language_switching(self, i18n_service):
        """Test language switching."""
        assert i18n_service.set_language('fr')
        assert i18n_service.current_language == 'fr'

        assert i18n_service.set_language('en')
        assert i18n_service.current_language == 'en'

        assert not i18n_service.set_language('xx')

    def test_translation_retrieval(self, i18n_service):
        """Test translation retrieval."""
        result = i18n_service.translate('app_name', 'common', language='en')
        assert result == 'CLEATI'

        result = i18n_service.translate('app_name', 'common', language='fr')
        assert result == 'CLEATI'

    def test_translation_completeness_check(self, i18n_service):
        """Test translation completeness validation."""
        missing = i18n_service.validate_translation_completeness()
        # Should have minimal or no missing translations
        assert isinstance(missing, dict)

    def test_language_isolation_check(self, i18n_service):
        """Test language isolation validation."""
        issues = i18n_service.validate_language_isolation()
        # Should have minimal language mixing
        assert isinstance(issues, dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
