# CLEATI V3.3 - Quick Deployment Commands

**Status**: Production Ready  
**Version**: 3.3.0  
**Date**: 2026-04-27  

---

## 🚀 Option 1: Docker Deployment (Recommended)

### Build the Docker Image
```bash
cd /path/to/CLEATI_V3.2
docker build -t cleati:v3.3-i18n .
```

### Run Single Container
```bash
docker run -d \
  --name cleati-v3.3 \
  -p 8000:8000 \
  -e DEFAULT_LANGUAGE=en \
  -e ENVIRONMENT=production \
  --restart unless-stopped \
  --health-cmd="curl -f http://localhost:8000/api/v3/health || exit 1" \
  --health-interval=30s \
  --health-timeout=3s \
  --health-retries=3 \
  cleati:v3.3-i18n
```

### Or Use Docker Compose (Recommended for Production)
```bash
cd /path/to/CLEATI_V3.2
docker-compose up -d
```

---

## ✅ Verify Deployment

### Check Container Status
```bash
docker ps | grep cleati
docker logs cleati-v3.3
```

### Test API Health
```bash
# Default language (English)
curl http://localhost:8000/api/v3/health

# Specific language via header
curl -H "X-Language: fr" http://localhost:8000/api/v3/health
curl -H "X-Language: es" http://localhost:8000/api/v3/health
curl -H "X-Language: de" http://localhost:8000/api/v3/health
curl -H "X-Language: it" http://localhost:8000/api/v3/health
curl -H "X-Language: pt" http://localhost:8000/api/v3/health
curl -H "X-Language: nl" http://localhost:8000/api/v3/health
curl -H "X-Language: pl" http://localhost:8000/api/v3/health

# Via query parameter
curl "http://localhost:8000/api/v3/health?language=fr"

# Get supported languages
curl http://localhost:8000/api/v3/languages
```

### Test Frontend
```bash
# Open in browser
http://localhost:8000

# Should display language selector with 8 buttons
# Languages should be selectable and UI should update
```

### Test Report Generation
```bash
# Create a project first
curl -X POST http://localhost:8000/api/v3/project/create \
  -H "X-Language: fr" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "budget": 50000,
    "sector": "technology"
  }'

# Generate report in French
curl -X POST http://localhost:8000/api/v3/project/1/report \
  -H "X-Language: fr" \
  -H "Content-Type: application/json" \
  -d '{"formats": ["pdf"]}'
```

---

## 🔍 Comprehensive Validation

### Script 1: Full Language Test
```bash
#!/bin/bash
echo "Testing all 8 languages..."

for lang in en fr es de it pt nl pl; do
  response=$(curl -s -H "X-Language: $lang" http://localhost:8000/api/v3/health)
  if echo "$response" | grep -q "\"language\":\"$lang\""; then
    echo "✓ $lang: OK"
  else
    echo "✗ $lang: FAILED"
    echo "Response: $response"
  fi
done
```

### Script 2: Performance Test
```bash
#!/bin/bash
echo "Performance Testing..."

# 100 requests
time for i in {1..100}; do
  curl -s -H "X-Language: fr" http://localhost:8000/api/v3/health > /dev/null
done

echo "Avg time per request should be <50ms"
```

### Script 3: Load Test
```bash
#!/bin/bash
# Install Apache Bench if needed: apt-get install apache2-utils

echo "Load Testing (100 concurrent requests, 1000 total)..."
ab -n 1000 -c 100 -H "X-Language: fr" http://localhost:8000/api/v3/health

echo ""
echo "Expected: 95%+ success rate, <200ms P99 response time"
```

---

## 📊 Real-Time Monitoring

### Monitor Container
```bash
# Watch logs in real-time
docker logs -f cleati-v3.3

# Watch resource usage
docker stats cleati-v3.3
```

### Monitor API
```bash
# Check every 5 seconds
watch -n 5 'curl -s -H "X-Language: fr" http://localhost:8000/api/v3/health | jq .'

# Or the included monitoring script
./logs/monitor.sh
```

---

## 🔧 Configuration

### Environment Variables
```bash
# Edit before running
export DEFAULT_LANGUAGE=en      # Default language
export ENVIRONMENT=production   # Environment
export API_PORT=8000           # API port
export DEBUG=false             # Debug mode
export LOG_LEVEL=info          # Logging level
```

### Change Default Language
```bash
# When starting container
docker run -d \
  --name cleati-v3.3 \
  -p 8000:8000 \
  -e DEFAULT_LANGUAGE=fr \
  cleati:v3.3-i18n
```

---

## 🆘 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs cleati-v3.3

# Check resource constraints
docker stats cleati-v3.3

# Try with more resources
docker run -d \
  --name cleati-v3.3 \
  -p 8000:8000 \
  --memory=1g \
  --cpus=1 \
  cleati:v3.3-i18n
```

### Slow response times
```bash
# Check container stats
docker stats cleati-v3.3

# Check if port is already in use
lsof -i :8000
# Kill if necessary: kill -9 <PID>

# Rebuild and redeploy
docker stop cleati-v3.3
docker rm cleati-v3.3
docker build -t cleati:v3.3-i18n .
docker run -d -p 8000:8000 cleati:v3.3-i18n
```

### Language not working
```bash
# Verify languages are configured
curl http://localhost:8000/api/v3/languages

# Check with header
curl -H "X-Language: fr" http://localhost:8000/api/v3/health

# Check logs for errors
docker logs cleati-v3.3 | grep -i language
```

---

## 🔄 Stopping & Cleanup

### Stop Container
```bash
docker stop cleati-v3.3
docker rm cleati-v3.3
```

### Stop with Docker Compose
```bash
docker-compose down
```

### View Stopped Containers
```bash
docker ps -a | grep cleati
```

### Remove Image
```bash
docker rmi cleati:v3.3-i18n
```

---

## 📈 Metrics to Track

After deployment, monitor these metrics:

```
✓ Error Rate: < 0.1% (alert if > 1%)
✓ Response Time P95: < 100ms (alert if > 500ms)
✓ Response Time P99: < 200ms (alert if > 1s)
✓ CPU Usage: 20-40% (alert if > 80%)
✓ Memory Usage: 50-70% (alert if > 85%)
✓ Requests/sec: Monitor baseline
✓ Language Distribution: Track usage by language
✓ Report Generation Time: < 5 seconds
✓ Translation Errors: 0 (alert if > 0)
```

---

## 🔐 Security Checklist

Before production deployment:

- [ ] Change default credentials
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up API authentication
- [ ] Configure CORS properly
- [ ] Implement rate limiting
- [ ] Set up security headers
- [ ] Enable audit logging
- [ ] Configure backups
- [ ] Set up monitoring alerts

---

## 📞 Support Resources

**Documentation**:
- DEPLOYMENT_READY_FINAL_REPORT.md - Comprehensive status
- PRODUCTION_DEPLOYMENT_CHECKLIST_I18N.md - Full checklist
- INTEGRATION_GUIDE_I18N.md - Integration steps
- README_DEPLOYMENT.md - Detailed guide

**Logs**:
- Container logs: `docker logs cleati-v3.3`
- Application logs: `./logs/deployment-*.log`
- Monitoring: `./logs/monitor.sh`

**Contact**: jfpitey@beseen360app.com

---

## 🎯 Deployment Status

**Ready**: ✅ YES  
**Version**: 3.3.0  
**Languages**: 8 (EN, FR, ES, DE, IT, PT, NL, PL)  
**Performance**: <1ms translation overhead  
**Status**: 🟢 PRODUCTION READY  

---

**Last Updated**: 2026-04-27  
**Next Review**: After first week in production  
