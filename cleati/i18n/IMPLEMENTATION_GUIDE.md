# CLEATI I18n Implementation Guide

## Overview

This guide covers the complete implementation of the internationalization (i18n) system for CLEATI V3.3. The system ensures strict language isolation across the UI, API, and reports, preventing any mixing of languages.

## Architecture

### Directory Structure

```
cleati/i18n/
├── config.json                          # Language configuration
├── __init__.py                          # Package initialization
├── generate_translations.py             # Translation generator
├── IMPLEMENTATION_GUIDE.md              # This file
│
├── translations/                        # Translation files
│   ├── fr/
│   │   ├── common.json                 # Common UI strings
│   │   ├── ui.json                     # UI component strings
│   │   ├── api.json                    # API messages
│   │   ├── reports.json                # Report section names
│   │   └── formats.json                # Date/number format strings
│   ├── en/
│   ├── es/
│   ├── de/
│   ├── it/
│   ├── pt/
│   ├── nl/
│   └── pl/
│
├── services/
│   └── i18n_service.py                 # Core I18nService class
│
├── middleware/
│   └── i18n_middleware.py              # FastAPI middleware & helpers
│
├── hooks/
│   ├── useTranslation.ts               # React hook for translations
│   └── useLocale.ts                    # React hook for formatting
│
├── integrations/
│   └── reports_i18n.py                 # Report generator i18n wrapper
│
└── tests/
    └── test_language_separation.py     # Comprehensive test suite
```

## Core Components

### 1. Configuration (config.json)

Defines all supported languages with locale-specific settings:

```json
{
  "languages": {
    "fr": {
      "name": "Français",
      "locale": "fr-FR",
      "dateFormat": "dd/MM/yyyy",
      "numberSeparator": ",",
      "thousandsSeparator": ".",
      "currencySymbol": "€",
      "currencyCode": "EUR"
    }
  },
  "defaultLanguage": "en",
  "fallbackLanguage": "en",
  "supportedNamespaces": ["common", "ui", "api", "reports", "formats"]
}
```

### 2. Translation Files

Each language has 5 namespaces:

- **common.json**: Core UI strings (buttons, labels, status messages)
- **ui.json**: Component-specific strings (navigation, forms, sections)
- **api.json**: API response messages (success, error, validation)
- **reports.json**: Report section titles and headers
- **formats.json**: Date/time/number format strings and month/day names

Example structure:
```json
{
  "app_name": "CLEATI",
  "welcome": "Welcome to CLEATI",
  "logout": "Logout",
  "save": "Save"
}
```

### 3. I18nService (services/i18n_service.py)

Core service class for all translation and localization operations.

#### Initialization
```python
from cleati.i18n import get_i18n_service

# Get singleton instance
i18n = get_i18n_service('/path/to/i18n')
```

#### Translation
```python
# Simple translation
message = i18n.translate('app_name')  # "CLEATI"

# With namespace
label = i18n.translate('project_name', 'ui')

# With parameters
greeting = i18n.translate(
    'greeting',
    'common',
    params={'name': 'John'}
)

# Shorthand
from cleati.i18n import t
message = t('app_name')
```

#### Language Management
```python
# Get supported languages
languages = i18n.get_supported_languages()

# Switch language
success = i18n.set_language('fr')

# Get current language
current = i18n.current_language
```

#### Localization
```python
from datetime import datetime

# Format date
date_str = i18n.format_date(datetime.now(), 'long')
# Output (FR): "dimanche, 26 avril 2026"

# Format number
num_str = i18n.format_number(1234.56, decimals=2)
# Output (FR): "1.234,56"

# Format currency
curr_str = i18n.format_currency(1000.00, 'EUR')
# Output (FR): "1000.00 €"
```

#### Validation
```python
# Check translation completeness
missing = i18n.validate_translation_completeness()

# Check language isolation
issues = i18n.validate_language_isolation()
```

### 4. FastAPI Integration (middleware/i18n_middleware.py)

#### Middleware Setup
```python
from fastapi import FastAPI
from cleati.i18n import get_i18n_service, I18nMiddleware

app = FastAPI()
i18n = get_i18n_service()

# Add middleware
app.add_middleware(I18nMiddleware, i18n_service=i18n)
```

#### Language Selection Priority
1. `X-Language` header
2. `language` query parameter
3. `Accept-Language` header

Example requests:
```bash
# Header
curl -H "X-Language: fr" http://api.example.com/api/v3/project

# Query parameter
curl "http://api.example.com/api/v3/project?language=es"

# Accept-Language header (auto)
curl -H "Accept-Language: de" http://api.example.com/api/v3/project
```

#### Response Helper
```python
from fastapi import Request
from cleati.i18n import I18nResponse, translate_for_response

@app.post("/api/v3/project/create")
async def create_project(request: Request, data: dict):
    # Create project...
    response = I18nResponse(request)
    return response.success('project_created', 'api', project_id='123')

# Output:
# {
#   "status": "success",
#   "message": "Projet créé avec succès",
#   "language": "fr",
#   "project_id": "123"
# }
```

#### Error Handling
```python
from cleati.i18n import I18nAwareException

raise I18nAwareException(
    status_code=404,
    message_key='project_not_found',
    i18n=i18n,
    namespace='api'
)
```

### 5. React Integration (hooks/)

#### useTranslation Hook
```typescript
import { useTranslation } from '@/cleati/i18n/hooks/useTranslation';

function MyComponent() {
  const { t, language, setLanguage } = useTranslation();

  return (
    <div>
      <h1>{t('app_name')}</h1>
      <label>{t('project_name', 'ui')}</label>
      <select value={language} onChange={(e) => setLanguage(e.target.value)}>
        <option value="en">English</option>
        <option value="fr">Français</option>
      </select>
    </div>
  );
}
```

#### useLocale Hook
```typescript
import { useLocale } from '@/cleati/i18n/hooks/useLocale';

function MyComponent() {
  const { locale, formatDate, formatNumber, formatCurrency } = useLocale();

  return (
    <div>
      <p>{formatDate(new Date(), 'long')}</p>
      <p>{formatNumber(1234.56, 2)}</p>
      <p>{formatCurrency(1000.00, 'EUR')}</p>
    </div>
  );
}
```

### 6. Reports Integration (integrations/reports_i18n.py)

```python
from cleati.i18n import I18nReportsGenerator

# Wrap existing generator
i18n_generator = I18nReportsGenerator(i18n, base_generator)

# Generate reports in specific language
reports = i18n_generator.generate_all_formats(
    unified_data=project_data,
    formats=['pdf', 'excel', 'word'],
    language='fr'  # Reports will be in French
)

# Each report section is fully localized
# - Headers and labels are translated
# - Numbers use locale-specific formatting
# - Dates use locale-specific formatting
# - Currency symbols and positions respect locale
```

## Language Isolation Guarantees

The system ensures strict language separation through:

### 1. Isolated Translation Files
Each language has its own directory with independent JSON files. No shared translations between languages.

### 2. Namespace Separation
5 distinct namespaces prevent cross-contamination:
- UI strings separate from API messages
- Reports terminology separate from UI
- Formatting rules in dedicated namespace

### 3. Validation Tests
Comprehensive test suite (`test_language_separation.py`) validates:
- No missing keys across languages
- No mixing of character sets (é in non-French files)
- No hardcoded English in other languages
- Format consistency across locales
- Currency and number format correctness

Run tests:
```bash
pytest cleati/i18n/tests/test_language_separation.py -v
```

### 4. Runtime Checks
```python
# Validate at startup
issues = i18n.validate_language_isolation()
if issues:
    raise RuntimeError(f"Language mixing detected: {issues}")

completeness = i18n.validate_translation_completeness()
if completeness:
    raise RuntimeError(f"Missing translations: {completeness}")
```

## API Endpoint Examples

### 1. Creating Project (Localized)
```bash
# Request with French
curl -X POST http://api.example.com/api/v3/project/create \
  -H "X-Language: fr" \
  -H "Content-Type: application/json" \
  -d '{"name": "Mon Projet"}'

# Response
{
  "status": "success",
  "message": "Projet créé avec succès",
  "language": "fr",
  "project_id": "abc123"
}
```

### 2. Error Response (Localized)
```bash
# Request with German
curl http://api.example.com/api/v3/project/invalid \
  -H "X-Language: de"

# Response
{
  "status": "error",
  "message": "Projekt nicht gefunden",
  "code": 404,
  "language": "de"
}
```

### 3. Generating Report (Localized)
```bash
POST /api/v3/project/123/report
{
  "formats": ["pdf", "excel", "word"],
  "language": "pt"
}

# Returns Portuguese reports with:
# - Localized section titles
# - Portuguese date formatting (dd/MM/yyyy)
# - Portuguese number formatting (1.234,56)
# - Portuguese currency (amounts €)
```

## Implementation Checklist

### Backend
- [ ] Load I18nService in startup
- [ ] Add I18nMiddleware to FastAPI
- [ ] Update all API endpoints to use i18n
- [ ] Wrap ReportGenerator with I18nReportsGenerator
- [ ] Add language parameter to report endpoints
- [ ] Validate translations at startup
- [ ] Add i18n exception handlers

### Frontend
- [ ] Import and setup useTranslation hook
- [ ] Replace hardcoded strings with t() calls
- [ ] Add language selector component
- [ ] Import and setup useLocale hook
- [ ] Use locale formatting in all displays
- [ ] Test all languages in UI

### Testing
- [ ] Run language separation tests
- [ ] Test each language in UI
- [ ] Test API responses in each language
- [ ] Generate reports in each language
- [ ] Verify number/date/currency formatting
- [ ] Check for any hardcoded strings

### Deployment
- [ ] Include translation files in Docker image
- [ ] Set default language in config
- [ ] Document language support in API docs
- [ ] Add language headers to API documentation
- [ ] Monitor for missing translation keys in logs

## Adding New Languages

1. Create language directory:
```bash
mkdir -p cleati/i18n/translations/XX
```

2. Add locale to config.json:
```json
"xx": {
  "name": "Language Name",
  "nativeName": "Native Name",
  "locale": "xx-XX",
  "dateFormat": "dd/MM/yyyy",
  "numberSeparator": ".",
  "thousandsSeparator": ",",
  "currencySymbol": "€",
  "currencyPosition": "after",
  "currencyCode": "EUR"
}
```

3. Create translation files:
```bash
touch cleati/i18n/translations/xx/{common,ui,api,reports,formats}.json
```

4. Copy English templates and translate:
```bash
cp cleati/i18n/translations/en/common.json \
   cleati/i18n/translations/xx/common.json
# Edit xx version with translations
```

5. Validate:
```bash
pytest cleati/i18n/tests/test_language_separation.py::TestLanguageSeparation::test_all_languages_defined
```

## Best Practices

1. **Always use translation keys**: Never hardcode strings
2. **Namespace correctly**: Use appropriate namespace for context
3. **Test translations**: Verify all languages regularly
4. **Validate formats**: Ensure dates/numbers match locale
5. **Check parameters**: Use {placeholders} in translation strings
6. **Monitor logs**: Check for missing translation keys
7. **Update consistently**: When adding features, update all languages
8. **Respect layout**: Some languages need more space

## Troubleshooting

### Missing Translation Key
```python
# Check if key exists
if 'missing_key' not in i18n.translations[lang]['namespace']:
    print(f"Add missing_key to {lang} translations")
```

### Language Not Set
```python
# Verify language switching
if not i18n.set_language('fr'):
    print("Language 'fr' not supported")
    print(f"Available: {i18n.get_supported_languages()}")
```

### Format Issues
```python
# Check locale configuration
locale = i18n.get_locale_config('fr')
print(f"Date format: {locale['dateFormat']}")
print(f"Number separator: {locale['numberSeparator']}")
```

## Performance

- Translation files are loaded once at startup
- All translations cached in memory
- No file I/O during request processing
- Format conversion cached when possible
- Minimal overhead per translation call (~1ms)

## Security

- Translation keys are never user input
- No code injection through translations
- Translation files are read-only in production
- Language codes validated against whitelist
- No sensitive data in translation files

## Support

For issues or questions:
1. Check `test_language_separation.py` for examples
2. Review API middleware documentation
3. Check React hooks implementation
4. Validate translation files with tests
5. Monitor logs for missing key warnings
