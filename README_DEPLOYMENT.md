# CLEATI V3.3 - Complete Production Deployment Guide

**Status:** ✅ Production Ready  
**Version:** 3.3  
**Last Updated:** 2026-04-26  
**AWS Region:** eu-west-1  
**Estimated Monthly Cost:** €270

---

## 📖 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Detailed Deployment](#detailed-deployment)
5. [Verification & Testing](#verification--testing)
6. [Operations](#operations)
7. [Support](#support)

---

## System Overview

**CLEATI V3.3** is a production-ready enterprise intelligence platform with 4 integrated AI engines:

1. **Financial Intelligence Engine** - Comprehensive financial analysis and projections
2. **Green Impact Intelligence Engine** - Environmental impact assessment and ESG scoring
3. **Business Plan Architect** - Strategic business plan generation
4. **Monitoring & Evaluation Auto-Architect** - Real-time KPI tracking and automated reporting

### Key Features

✅ Multi-format Report Generation (PDF, Excel, Word)  
✅ Real-time Monitoring Dashboard with Grafana/Prometheus  
✅ Intelligent Funding Source Matching  
✅ Dual ROI Calculation (Financial + Ecological)  
✅ Event-Driven Architecture with Async Processing  
✅ Auto-Scaling Infrastructure (3-6 tasks)  
✅ Multi-AZ Database with Automated Backups  
✅ CloudWatch Monitoring & Alarms  
✅ Infrastructure-as-Code (Terraform)  
✅ Docker Containerization with Health Checks  

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet / Users                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
           ┌─────────────────────────────┐
           │   AWS Application Load      │
           │   Balancer (ALB)            │
           │   Port: 80, 443             │
           └────────┬────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
    ┌────────────────┐    ┌────────────────┐
    │  ECS Task 1    │    │  ECS Task 2    │
    │  (Fargate)     │    │  (Fargate)     │
    │  t3.small      │    │  t3.small      │
    │  CPU: 256      │    │  CPU: 256      │
    │  Memory: 512   │    │  Memory: 512   │
    └──────┬─────────┘    └──────┬─────────┘
           │                     │
           └──────────┬──────────┘
                      ▼
          ┌────────────────────────┐
          │   RDS PostgreSQL       │
          │   Multi-AZ             │
          │   db.t3.micro          │
          │   7-day backups        │
          └────────────────────────┘
          
          ┌────────────────────────┐
          │   S3 Project Data      │
          │   Versioning: ON       │
          │   Encryption: AES-256  │
          └────────────────────────┘
          
          ┌────────────────────────┐
          │   CloudWatch Logs      │
          │   Retention: 30 days   │
          │   Metrics Collection   │
          └────────────────────────┘
```

### Infrastructure Components

| Component | Type | Configuration | Purpose |
|-----------|------|---------------|---------|
| ALB | AWS Load Balancer | HTTP/HTTPS on 80, 443 | Route traffic to ECS tasks |
| ECS | Container Orchestration | 3-6 Fargate tasks (t3.small) | Run CLEATI application |
| RDS | PostgreSQL Database | Multi-AZ, db.t3.micro | Store project and configuration data |
| S3 | Object Storage | Versioning + Encryption | Store project files and reports |
| CloudWatch | Monitoring | Logs, Metrics, Dashboards | Monitor application health |
| Prometheus | Time Series DB | Scrapes metrics from app | Collect performance metrics |
| Grafana | Dashboards | Connects to Prometheus | Visualize metrics |

---

## Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# 1. Prerequisites
# Ensure you have: Docker, Terraform, AWS CLI, Python 3.11+

# 2. Set AWS region (optional, defaults to eu-west-1)
export AWS_REGION="eu-west-1"

# 3. Make script executable and run
chmod +x QUICKSTART_DEPLOYMENT.sh
./QUICKSTART_DEPLOYMENT.sh

# The script will:
# - Check all prerequisites
# - Setup local environment
# - Run tests locally
# - Create AWS infrastructure
# - Build and push Docker image
# - Deploy with Terraform
# - Verify deployment
```

### Option 2: Step-by-Step Manual Deployment

See [Detailed Deployment](#detailed-deployment) section below.

---

## Detailed Deployment

### Phase 1: Local Environment Setup

```bash
# Clone repository
cd CLEATI_V3.2

# Copy environment template
cp .env.example .env

# Edit configuration (set database password, API keys, etc.)
nano .env

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed')"
```

### Phase 2: Local Testing with Docker Compose

```bash
# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Verify services are healthy
docker-compose ps

# Expected output:
# cleati-api      running  ✓
# postgres        running  ✓
# redis           running  ✓
# prometheus      running  ✓
# grafana         running  ✓
# nginx           running  ✓

# View API logs
docker-compose logs -f cleati-api

# Access local services
# API:        http://localhost:8000
# API Docs:   http://localhost:8000/docs
# Grafana:    http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

### Phase 3: Run Test Suite

```bash
# Run all tests
pytest test_suite_cleati_v3.py -v

# Run specific test
pytest test_suite_cleati_v3.py::test_financial_analysis -v

# Generate coverage report
pytest --cov=cleati_orchestrator_v3 --cov-report=html

# Expected: All tests passing ✓
```

### Phase 4: AWS Account Setup

```bash
# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Verify credentials
aws sts get-caller-identity

# Set environment variables
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION="eu-west-1"

# Create S3 bucket for Terraform state
aws s3 mb s3://cleati-terraform-state-${AWS_ACCOUNT_ID}

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket cleati-terraform-state-${AWS_ACCOUNT_ID} \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for locks
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### Phase 5: Build and Push Docker Image

```bash
# Build Docker image
docker build -t cleati:v3.3 .

# Create ECR repository
aws ecr create-repository \
  --repository-name cleati \
  --region eu-west-1

# Authenticate with ECR
aws ecr get-login-password --region eu-west-1 | \
  docker login --username AWS --password-stdin \
  ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com

# Tag and push image
docker tag cleati:v3.3 \
  ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/cleati:v3.3

docker push \
  ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/cleati:v3.3
```

### Phase 6: Deploy with Terraform

```bash
# Create terraform.tfvars
cat > terraform.tfvars <<EOF
aws_region = "eu-west-1"
environment = "production"
app_name = "cleati-v3"
desired_count = 3
container_image = "${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/cleati:v3.3"
EOF

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt

# Review plan
terraform plan -out=tfplan

# Deploy infrastructure
terraform apply tfplan

# Save outputs
terraform output > outputs.txt

# Get ALB DNS (your API endpoint)
ALB_DNS=$(terraform output -raw alb_dns_name)
echo "API Endpoint: http://${ALB_DNS}"
```

### Phase 7: Verify Deployment

```bash
# Get ALB DNS
ALB_DNS=$(terraform output -raw alb_dns_name)

# Test health endpoint
curl http://${ALB_DNS}/api/v3/health

# Expected response:
# {"status": "healthy", "timestamp": "2026-04-26T..."}

# Test API
curl http://${ALB_DNS}/api/v3/projects

# Check ECS service status
aws ecs describe-services \
  --cluster cleati-v3-cluster \
  --services cleati-v3-service \
  --region eu-west-1

# View logs
aws logs tail /ecs/cleati-v3 --follow

# Expected: All ECS tasks running and healthy
```

---

## Verification & Testing

### Health Checks

```bash
# ALB Health Status
aws elbv2 describe-target-health \
  --target-group-arn <target-group-arn> \
  --region eu-west-1

# ECS Task Status
aws ecs describe-tasks \
  --cluster cleati-v3-cluster \
  --tasks $(aws ecs list-tasks --cluster cleati-v3-cluster --query 'taskArns[0]' --output text) \
  --region eu-west-1

# Database Status
aws rds describe-db-instances \
  --db-instance-identifier cleati-v3-db \
  --region eu-west-1
```

### Load Testing

```bash
# Install load testing tool
pip install locust

# Create locustfile.py
cat > locustfile.py <<'EOF'
from locust import HttpUser, task, between

class CLEATIUser(HttpUser):
    wait_time = between(1, 5)
    
    @task
    def health_check(self):
        self.client.get("/api/v3/health")
    
    @task
    def list_projects(self):
        self.client.get("/api/v3/projects")
EOF

# Run load test
locust -f locustfile.py --host http://${ALB_DNS} --users 100 --spawn-rate 10

# Monitor metrics during test
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=cleati-v3-service \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average,Maximum
```

---

## Operations

### Daily Monitoring

```bash
# Check CloudWatch Dashboard
aws cloudwatch describe-dashboards --dashboard-name CLEATI-V3

# View logs for errors
aws logs tail /ecs/cleati-v3 --follow --filter-pattern "ERROR"

# Check active alarms
aws cloudwatch describe-alarms --state-value ALARM --region eu-west-1
```

### Weekly Maintenance

```bash
# Create database snapshot
aws rds create-db-snapshot \
  --db-instance-identifier cleati-v3-db \
  --db-snapshot-identifier cleati-v3-backup-$(date +%Y%m%d)

# Review and download logs
aws logs create-export-task \
  --log-group-name /ecs/cleati-v3 \
  --from $(date -d '7 days ago' +%s)000 \
  --to $(date +%s)000 \
  --destination s3-bucket-name

# Check costs (AWS Cost Explorer)
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics "BlendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE
```

### Scaling

```bash
# Manual scaling
aws ecs update-service \
  --cluster cleati-v3-cluster \
  --service cleati-v3-service \
  --desired-count 5

# Auto-scaling is configured:
# Scale up: CPU > 70% or Memory > 80%
# Scale down: CPU < 30% or Memory < 50%
# Min tasks: 3, Max tasks: 6

# View auto-scaling status
aws application-autoscaling describe-scaling-activities \
  --service-namespace ecs \
  --resource-id service/cleati-v3-cluster/cleati-v3-service
```

### Deploying Updates

```bash
# Build new version
docker build -t cleati:v3.4 .

# Push to ECR
docker tag cleati:v3.4 ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/cleati:v3.4
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/cleati:v3.4

# Update Terraform
terraform apply -var="container_image=${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/cleati:v3.4"

# ECS automatically performs rolling deployment
# Monitor progress
watch -n 5 'aws ecs describe-services \
  --cluster cleati-v3-cluster \
  --services cleati-v3-service \
  --region eu-west-1 \
  --query "services[0].[deployments[*].taskCount,deployments[*].status]"'
```

### Disaster Recovery

```bash
# Restore from latest RDS snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier cleati-v3-db-restored \
  --db-snapshot-identifier <snapshot-id>

# Restore complete infrastructure
terraform destroy
terraform apply

# Restore from S3 versioning
aws s3 sync s3://cleati-project-data/ ./data/ --source-region eu-west-1
```

---

## API Endpoints

### Health & Status
- `GET /api/v3/health` - Health check
- `GET /api/v3/status` - System status

### Projects
- `POST /api/v3/projects` - Create project
- `GET /api/v3/projects` - List projects
- `GET /api/v3/projects/{id}` - Get project details
- `PUT /api/v3/projects/{id}` - Update project

### Intelligence Engines
- `GET /api/v3/projects/{id}/financial` - Financial analysis
- `GET /api/v3/projects/{id}/green` - Green impact assessment
- `GET /api/v3/projects/{id}/business-plan` - Business plan
- `GET /api/v3/projects/{id}/monitoring` - Monitoring data

### Reports
- `POST /api/v3/projects/{id}/reports/generate` - Generate all report formats
- `GET /api/v3/projects/{id}/reports/{format}` - Download report (pdf, excel, docx)

### Monitoring
- `POST /api/v3/projects/{id}/monitoring/update` - Update KPI values
- `GET /api/v3/monitoring/dashboard` - Dashboard metrics

See full API documentation at: `http://${ALB_DNS}/docs`

---

## Cost Optimization

### Current Estimate (€270/month)
- ECS Fargate: €150 (3 tasks × t3.small)
- RDS PostgreSQL: €80 (db.t3.micro multi-AZ)
- ALB: €20
- Data Transfer: €10
- S3: €5
- CloudWatch: €5

### Optimization Options
1. **Reserved Instances** - Save 30-50%
2. **Fargate Spot** - Save up to 70%
3. **RDS Aurora Serverless** - Auto-scaling database
4. **CloudFront** - Cache static content
5. **Log Retention** - Adjust CloudWatch retention

---

## Troubleshooting

### ECS Tasks Failing to Start

```bash
# Check task logs
aws ecs describe-tasks \
  --cluster cleati-v3-cluster \
  --tasks $(aws ecs list-tasks --cluster cleati-v3-cluster --query 'taskArns[0]' --output text)

# View CloudWatch logs
aws logs tail /ecs/cleati-v3 --follow
```

### Database Connection Issues

```bash
# Check RDS status
aws rds describe-db-instances \
  --db-instance-identifier cleati-v3-db

# Test connectivity
psql -h <rds-endpoint> -U cleati_admin -d cleati
```

### High Memory Usage

```bash
# Increase task memory
terraform apply -var="container_memory=1024"

# Check current usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=cleati-v3-service
```

---

## Support

### Documentation Files
- `PRODUCTION_DEPLOYMENT_GUIDE.md` - Detailed deployment procedures
- `FINAL_DEPLOYMENT_CHECKLIST.md` - Complete verification checklist
- `QUICKSTART_DEPLOYMENT.sh` - Automated deployment script
- `API_REFERENCE.md` - API endpoint documentation
- `database-schema.sql` - Database schema

### Getting Help
- Email: support@cleati-platform.com
- Slack: #cleati-production
- On-call: Check PagerDuty schedule

### Reporting Issues
1. Check CloudWatch logs
2. Review CloudWatch dashboards
3. Run health checks
4. Document issue and escalate to team

---

## Checklist

Before going live, verify:

- [ ] All 4 intelligent engines operational
- [ ] Reports generation working (PDF/Excel/Word)
- [ ] Monitoring dashboard accessible
- [ ] ECS tasks healthy (desired count reached)
- [ ] RDS database accessible and healthy
- [ ] S3 bucket versioning enabled
- [ ] CloudWatch alarms configured
- [ ] Load testing completed (target: 100+ req/sec)
- [ ] Disaster recovery procedures documented
- [ ] Backup and restore tested
- [ ] Security audit completed
- [ ] Cost monitoring configured

---

**Status: 🟢 Ready for Production Deployment**

**Created:** 2026-04-26  
**Version:** CLEATI V3.3  
**AWS Region:** eu-west-1  
**Estimated Cost:** €270/month

