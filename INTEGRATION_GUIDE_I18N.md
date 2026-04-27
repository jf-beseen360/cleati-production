# CLEATI V3.3 - I18n Integration Guide

Complete guide for integrating the i18n system into your existing CLEATI installation.

## Overview

This guide shows how to migrate from the base API to the i18n-integrated version with full multi-language support across all endpoints and the frontend UI.

---

## Phase 1: Preparation

### 1.1 Backup Current System

```bash
# Backup existing API
cp cleati_production_api_v3.py cleati_production_api_v3.backup.py

# Backup existing interface
cp cleati_interface_v3.html cleati_interface_v3.backup.html
```

### 1.2 Verify I18n Files

```bash
# Check i18n installation
ls -la cleati/i18n/config.json
ls -la cleati/i18n/services/i18n_service.py
ls -la cleati/i18n/middleware/i18n_middleware.py
ls -la cleati/i18n/translations/

# Expected: 40 translation files (8 languages × 5 namespaces)
find cleati/i18n/translations -name "*.json" | wc -l
# Output: 40
```

---

## Phase 2: API Integration

### 2.1 Replace API File

```bash
# Option 1: Replace entire API
cp cleati_production_api_v3_i18n.py cleati_production_api_v3.py

# Option 2: Manual integration (if you have customizations)
# Copy I18n imports and initialization code
# Copy middleware setup
# Update endpoints one by one
```

### 2.2 Update Requirements

Add these to your `requirements.txt` if not already present:

```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
```

Install:
```bash
pip install -r requirements.txt --break-system-packages
```

### 2.3 Initialize I18n at Startup

Create `startup.py`:

```python
from cleati.i18n import get_i18n_service

def initialize_i18n():
    """Initialize i18n system at application startup."""
    i18n = get_i18n_service()

    print("🌍 I18n System Status:")
    print(f"✓ Supported languages: {len(i18n.get_supported_languages())}")

    # Validate translations
    issues = i18n.validate_language_isolation()
    if issues:
        print(f"⚠️  Language mixing detected: {issues}")

    missing = i18n.validate_translation_completeness()
    if missing:
        print(f"⚠️  Missing translations: {missing}")

    return i18n

if __name__ == "__main__":
    initialize_i18n()
```

### 2.4 Test API with i18n

```bash
# Start API
python -m uvicorn cleati_production_api_v3:app --reload

# Test English (default)
curl http://localhost:8000/api/v3/health
# Output: {"status": "healthy", "language": "en", ...}

# Test French
curl -H "X-Language: fr" http://localhost:8000/api/v3/health
# Output: {"status": "healthy", "language": "fr", ...}

# Test Spanish (via query param)
curl "http://localhost:8000/api/v3/health?language=es"
# Output: {"status": "healthy", "language": "es", ...}
```

---

## Phase 3: Frontend Integration

### 3.1 Replace Interface File

```bash
# Replace HTML interface
cp cleati_interface_v3_i18n.html cleati_interface_v3.html
```

### 3.2 Serve Static Files

Update your API to serve the HTML:

```python
# In cleati_production_api_v3.py
from fastapi.staticfiles import StaticFiles

# Uncomment or add:
app.mount("/static", StaticFiles(directory="static"), name="static")

# Or serve HTML as root
@app.get("/")
async def root(request: Request):
    # Returns welcome message in user's language
    ...
```

### 3.3 Test Frontend

```bash
# Navigate to http://localhost:8000
# You should see:
# - Language selector (FR, EN, ES, DE, IT, PT, NL, PL)
# - All UI text updated based on selected language
# - Project creation form
# - Localized metrics and sections
```

---

## Phase 4: Database/Storage Integration

### 4.1 Store User Language Preference

```python
# In user/session model
class UserSession:
    user_id: str
    preferred_language: str = "en"  # Default
    created_at: datetime
    updated_at: datetime
```

### 4.2 Load Language from Session

```python
@app.post("/api/v3/user/set-language")
async def set_user_language(request: Request, language: str):
    """Store user's language preference."""
    user_id = request.headers.get("X-User-ID")
    # Store in database
    # user.preferred_language = language
    # db.save(user)

    return {
        "status": "success",
        "message": f"Language set to {language}",
        "language": language
    }
```

---

## Phase 5: Report Integration

### 5.1 Update Report Endpoint

```python
# Reports are already localized in new API
# Just test:

curl -X POST http://localhost:8000/api/v3/project/123/report \
  -H "X-Language: fr" \
  -H "Content-Type: application/json" \
  -d '{
    "formats": ["pdf", "excel", "word"],
    "language": "fr"
  }'
```

### 5.2 Test Localized Reports

```bash
# Generate French report
curl -X POST http://localhost:8000/api/v3/project/123/report \
  -H "X-Language: fr" \
  -d '{"formats": ["pdf"]}'

# Get download link
# POST response includes:
# "download_endpoints": {
#   "pdf": "/api/v3/project/123/report/pdf?language=fr"
# }

# Download
curl http://localhost:8000/api/v3/project/123/report/pdf?language=fr \
  -o CLEATI_Report_123_fr.pdf
```

---

## Phase 6: Docker Integration

### 6.1 Update Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy i18n files FIRST
COPY cleati/i18n /app/cleati/i18n

# Copy application files
COPY cleati_*.py /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy HTML interface
COPY cleati_interface_v3_i18n.html /app/static/index.html

# Set default language
ENV DEFAULT_LANGUAGE=en

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD curl -f http://localhost:8000/api/v3/health || exit 1

CMD ["python", "-m", "uvicorn", "cleati_production_api_v3:app", \
     "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Build and Run

```bash
# Build image
docker build -t cleati:v3.3-i18n .

# Run container
docker run -p 8000:8000 \
  -e DEFAULT_LANGUAGE=fr \
  cleati:v3.3-i18n

# Test
curl http://localhost:8000/api/v3/health
```

### 6.3 Docker Compose (Optional)

```yaml
version: '3.8'

services:
  cleati-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEFAULT_LANGUAGE=en
      - LOG_LEVEL=info
    volumes:
      - ./cleati:/app/cleati
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v3/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=cleati
      - POSTGRES_USER=cleati
      - POSTGRES_PASSWORD=cleati
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Phase 7: Configuration

### 7.1 Environment Variables

```bash
# .env file
DEFAULT_LANGUAGE=en
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
DEBUG=false

# Optional
DATABASE_URL=postgresql://user:pass@localhost/cleati
REDIS_URL=redis://localhost:6379/0
```

### 7.2 Load Configuration

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    default_language: str = "en"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "info"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Phase 8: Testing

### 8.1 API Tests

```bash
#!/bin/bash

echo "Testing CLEATI V3.3 I18n Integration"
echo "====================================="

# Test English
echo "Testing English..."
curl -s -H "X-Language: en" http://localhost:8000/api/v3/health | grep "en"

# Test French
echo "Testing French..."
curl -s -H "X-Language: fr" http://localhost:8000/api/v3/health | grep "fr"

# Test Spanish
echo "Testing Spanish..."
curl -s -H "X-Language: es" http://localhost:8000/api/v3/health | grep "es"

# Test unsupported language (should fallback)
echo "Testing unsupported language..."
curl -s -H "X-Language: xx" http://localhost:8000/api/v3/health

echo "All tests completed!"
```

### 8.2 Frontend Tests

```javascript
// In browser console
// Test 1: Language switching
document.querySelector('.lang-btn').click();
console.log("✓ Language selector works");

// Test 2: Form submission
document.getElementById('projectName').value = "Test Project";
document.getElementById('budget').value = "50000";
document.getElementById('setupForm').submit();
// Should create project with localized response

// Test 3: Metrics display
document.querySelector('[data-tab="financial"]').click();
console.log("✓ Tab navigation works");
```

### 8.3 Validation Tests

```bash
# Run language isolation tests
cd cleati/i18n
python -m pytest tests/test_language_separation.py -v

# Or manually validate
python3 << 'EOF'
import json
import os

config = json.load(open('config.json'))
print(f"✓ {len(config['languages'])} languages configured")
print(f"✓ {len(config['supportedNamespaces'])} namespaces")

# Check translation files
total_files = 0
for lang in config['languages'].keys():
    for ns in config['supportedNamespaces']:
        path = f'translations/{lang}/{ns}.json'
        if os.path.exists(path):
            total_files += 1

print(f"✓ {total_files} translation files present")
EOF
```

---

## Phase 9: Deployment

### 9.1 Pre-Deployment Checklist

```
✓ API fully tested with i18n
✓ Frontend loads and shows language selector
✓ All 8 languages working
✓ Reports generate in all languages
✓ Docker image builds successfully
✓ Environment variables configured
✓ Database migrations complete (if needed)
✓ Language isolation validated
✓ Performance benchmarked
✓ Documentation updated
```

### 9.2 Staging Deployment

```bash
# Deploy to staging
git checkout -b feature/i18n-integration
git add cleati_production_api_v3.py cleati_interface_v3_i18n.html
git commit -m "feat: integrate i18n system with 8 languages"
git push origin feature/i18n-integration

# Create pull request and run CI/CD tests
```

### 9.3 Production Deployment

```bash
# Merge to main after approval
git checkout main
git merge feature/i18n-integration
git push origin main

# Deploy using your CI/CD pipeline
# AWS: `aws ecs update-service --cluster cleati --service cleati-api`
# Or manually:
docker push cleati:v3.3-i18n
kubectl set image deployment/cleati-api cleati-api=cleati:v3.3-i18n

# Verify deployment
curl https://api.cleati.com/api/v3/health
curl -H "X-Language: fr" https://api.cleati.com/api/v3/health
```

---

## Phase 10: Monitoring & Maintenance

### 10.1 Monitor Language Usage

```python
# Log language usage
@app.middleware("http")
async def log_language_usage(request: Request, call_next):
    language = getattr(request.state, 'language', 'en')
    # Log to analytics
    # analytics.track('language_used', {'language': language})

    response = await call_next(request)
    return response
```

### 10.2 Check for Missing Translations

```python
# At startup
issues = i18n.validate_language_isolation()
missing = i18n.validate_translation_completeness()

if issues or missing:
    logger.warning(f"Translation issues: {issues} {missing}")
    # Send alert to monitoring system
```

### 10.3 Performance Monitoring

```bash
# Monitor API response times
ab -n 1000 -c 10 -H "X-Language: fr" http://localhost:8000/api/v3/health

# Expected: <50ms average response time
# i18n overhead: <1ms
```

---

## Rollback Plan

If issues occur:

### 10.1 Quick Rollback

```bash
# Revert to backup
cp cleati_production_api_v3.backup.py cleati_production_api_v3.py
cp cleati_interface_v3.backup.html cleati_interface_v3.html

# Restart service
docker restart cleati-api
# or
pm2 restart cleati-api
```

### 10.2 Known Issues & Fixes

| Issue | Solution |
|-------|----------|
| Language not detected | Check `X-Language` header or `?language=` param |
| Missing translation key | Add key to all language JSON files |
| Report generation fails | Ensure i18n_reports initialized correctly |
| Frontend doesn't translate | Check API is returning localized responses |
| Performance degradation | Validate translation file sizes, check caching |

---

## Support & Troubleshooting

### Common Issues

**1. "Language 'xx' not supported"**
```bash
# Check supported languages
curl http://localhost:8000/api/v3/languages

# Should return 8 languages
```

**2. "Translation key missing"**
```bash
# Check translation file
grep "missing_key" cleati/i18n/translations/*/common.json

# Add missing key to all language files
```

**3. "Report generation timeout"**
```python
# Increase timeout in API
@app.post("/api/v3/project/{project_id}/report")
async def generate_report(...):
    # Set timeout
    timeout = 60  # seconds
    ...
```

**4. "CORS errors"**
```python
# Ensure X-Language in CORS headers
app.add_middleware(
    CORSMiddleware,
    allow_headers=["*", "X-Language"],
    ...
)
```

---

## Performance Baseline

Expected metrics after i18n integration:

| Metric | Expected | Actual |
|--------|----------|--------|
| API startup time | +100ms | - |
| Translation lookup | <1ms | - |
| Report generation | +50ms | - |
| Memory overhead | +2MB | - |
| Request overhead | <5ms | - |

---

## Success Criteria

✅ All 8 languages working  
✅ <50ms API response time  
✅ Reports localized  
✅ Frontend responsive  
✅ No errors in logs  
✅ User language preferences persisted  
✅ Analytics tracking enabled  
✅ Monitoring alerts configured  

---

## Next Steps

1. **Week 1**: Complete Phase 1-3 (Preparation, API, Frontend)
2. **Week 2**: Complete Phase 4-5 (Database, Reports)
3. **Week 3**: Complete Phase 6-8 (Docker, Configuration, Testing)
4. **Week 4**: Complete Phase 9-10 (Deployment, Monitoring)

---

**Document Version:** 1.0  
**Last Updated:** 2026-04-26  
**Status:** Production Ready
