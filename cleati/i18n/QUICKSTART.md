# CLEATI I18n Quick Start

Get up and running with multi-language support in 5 minutes.

## Installation

Translation files and service are ready to use:

```bash
# No installation needed - files are in cleati/i18n/
# Just import and use
```

## Backend Usage (FastAPI)

### 1. Setup Middleware
```python
from fastapi import FastAPI
from cleati.i18n import get_i18n_service, I18nMiddleware

app = FastAPI()
i18n = get_i18n_service()

# Add middleware - handles language detection automatically
app.add_middleware(I18nMiddleware, i18n_service=i18n)
```

### 2. Use in Endpoints
```python
from fastapi import Request
from cleati.i18n import I18nResponse

@app.post("/api/v3/project/create")
async def create_project(request: Request, data: dict):
    project_id = "123"
    
    # Create response helper
    response = I18nResponse(request)
    
    # Return localized response
    return response.success('project_created', 'api', project_id=project_id)
```

### 3. Test It
```bash
# English (default)
curl http://localhost:8000/api/v3/project/create

# French
curl -H "X-Language: fr" http://localhost:8000/api/v3/project/create

# Spanish (via query param)
curl "http://localhost:8000/api/v3/project/create?language=es"
```

## Frontend Usage (React)

### 1. Setup
```typescript
import { useTranslation } from '@/cleati/i18n/hooks/useTranslation';
import { useLocale } from '@/cleati/i18n/hooks/useLocale';

function App() {
  const { t, setLanguage, language } = useTranslation();
  const { formatCurrency, formatDate } = useLocale();

  return (
    <div>
      <h1>{t('app_name')}</h1>
      {/* Language selector */}
      <select value={language} onChange={(e) => setLanguage(e.target.value)}>
        <option value="en">English</option>
        <option value="fr">Français</option>
        <option value="es">Español</option>
      </select>
    </div>
  );
}
```

### 2. Use Translations
```typescript
// Simple translation
<h1>{t('app_name')}</h1>

// From specific namespace
<label>{t('project_name', 'ui')}</label>

// With parameters
<p>{t('greeting', 'common', { name: 'John' })}</p>
```

### 3. Format Numbers and Dates
```typescript
const { formatDate, formatNumber, formatCurrency } = useLocale();

<span>{formatDate(new Date(), 'long')}</span>
<span>{formatNumber(1234.56, 2)}</span>
<span>{formatCurrency(1000.00)}</span>
```

## API Response Examples

### Success Response
```bash
curl -H "X-Language: fr" http://localhost:8000/api/v3/project/create

{
  "status": "success",
  "message": "Projet créé avec succès",
  "language": "fr",
  "project_id": "123"
}
```

### Error Response
```bash
curl -H "X-Language: de" http://localhost:8000/api/v3/project/invalid

{
  "status": "error",
  "message": "Projekt nicht gefunden",
  "code": 404,
  "language": "de"
}
```

## Supported Languages

| Code | Language | Native |
|------|----------|--------|
| en | English | English |
| fr | French | Français |
| es | Spanish | Español |
| de | German | Deutsch |
| it | Italian | Italiano |
| pt | Portuguese | Português |
| nl | Dutch | Nederlands |
| pl | Polish | Polski |

## Common Use Cases

### 1. Get Localized Dates
```python
from cleati.i18n import get_i18n_service
from datetime import datetime

i18n = get_i18n_service()
i18n.set_language('fr')

# Format for French user
date_str = i18n.format_date(datetime.now(), 'long')
# Output: "dimanche, 26 avril 2026"
```

### 2. Get Localized Numbers
```python
i18n.set_language('de')

# Format for German user
num_str = i18n.format_number(1234567.89)
# Output: "1.234.567,89"
```

### 3. Get Localized Currency
```python
i18n.set_language('pt')

# Format for Portuguese user
curr_str = i18n.format_currency(1000.00, 'EUR')
# Output: "1000.00 €"
```

### 4. Validate Languages
```python
from cleati.i18n import get_i18n_service

i18n = get_i18n_service()

# Get all supported languages
languages = i18n.get_supported_languages()
# [
#   {'code': 'en', 'name': 'English', ...},
#   {'code': 'fr', 'name': 'French', ...},
#   ...
# ]

# Check if language is supported
if i18n.set_language('xx'):
    print("Language supported")
else:
    print("Language not supported")
```

### 5. Generate Localized Reports
```python
from cleati.i18n import I18nReportsGenerator

# Initialize with i18n
i18n_reports = I18nReportsGenerator(i18n, base_generator)

# Generate French report
pdf_bytes = i18n_reports.generate_all_formats(
    project_data,
    formats=['pdf'],
    language='fr'
)
```

## Localized API Endpoint

```python
from fastapi import Request
from cleati.i18n import I18nResponse

@app.post("/api/v3/project/{project_id}/report")
async def generate_report(request: Request, project_id: str, formats: list):
    """Generate localized report"""
    response = I18nResponse(request)
    
    # Get language from request
    language = request.state.language
    
    # Generate report in user's language
    reports = i18n_reports.generate_all_formats(
        project_data,
        formats=formats,
        language=language
    )
    
    return response.success(
        'report_generated',
        'api',
        report_formats=list(reports.keys())
    )
```

## Docker Integration

Translations are included in the Docker image:

```dockerfile
# In Dockerfile
COPY cleati/i18n /app/cleati/i18n

# Set default language
ENV DEFAULT_LANGUAGE=en
```

## Testing

Run all tests:
```bash
pytest cleati/i18n/tests/test_language_separation.py -v
```

Test specific language:
```bash
pytest cleati/i18n/tests/test_language_separation.py::TestLanguageSeparation::test_translation_completeness -v
```

## Troubleshooting

### Missing Translation
```
KeyError: 'some_key' not found in namespace 'ui'
```
Solution: Add the key to all language files in `translations/{lang}/ui.json`

### Language Not Set
```
Language 'xx' not supported
```
Solution: Check supported languages with `i18n.get_supported_languages()`

### Wrong Format
```
Expected French number "1.234,56" but got "1234.56"
```
Solution: Use `i18n.format_number()` instead of Python's default formatting

## Next Steps

1. **Review**: Read `IMPLEMENTATION_GUIDE.md` for detailed documentation
2. **Implement**: Add i18n to your endpoints
3. **Test**: Run test suite to validate translations
4. **Deploy**: Include i18n files in your deployment
5. **Monitor**: Check logs for missing translation keys

## Performance Tips

1. I18nService is a singleton - initialized once at startup
2. Translations are cached in memory - no file I/O during requests
3. Format operations are optimized - minimal CPU overhead
4. Use language parameter in requests to avoid re-initialization

## API Documentation

All endpoints support language selection:

```bash
# Via header (recommended for APIs)
curl -H "X-Language: fr" https://api.example.com/api/v3/project

# Via query parameter
curl "https://api.example.com/api/v3/project?language=es"

# Via Accept-Language (auto-detected)
curl -H "Accept-Language: de" https://api.example.com/api/v3/project
```

Response always includes language info:
```json
{
  "status": "success",
  "message": "Translated message",
  "language": "fr"
}
```

---

**Ready to go!** Start using i18n in your endpoints and components.
