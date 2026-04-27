# CLEATI V3.3 - Production Deployment Guide

## Overview

This guide covers complete production deployment of CLEATI V3.3 on AWS with infrastructure-as-code (Terraform), containerization (Docker), and monitoring.

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
           └────────┬────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
    ┌────────────┐        ┌────────────┐
    │  ECS Task  │ ─────► │  ECS Task  │
    │ (Fargate)  │        │ (Fargate)  │
    └──────┬─────┘        └──────┬─────┘
           │                     │
           └──────────┬──────────┘
                      ▼
          ┌────────────────────────┐
          │   RDS PostgreSQL       │
          │   (Multi-AZ)           │
          └────────────────────────┘
          
          ┌────────────────────────┐
          │   S3 Project Data      │
          └────────────────────────┘
          
          ┌────────────────────────┐
          │   CloudWatch Logs      │
          │   & Monitoring         │
          └────────────────────────┘
```

## Prerequisites

### Local Development
- Docker
- Docker Compose
- AWS CLI v2
- Terraform v1.0+
- Python 3.11+
- PostgreSQL client

### AWS Account
- AWS account with appropriate permissions
- AWS credentials configured locally
- S3 bucket for Terraform state
- DynamoDB table for Terraform locks

## Phase 1: Local Development Setup

### 1.1 Clone & Setup

```bash
cd CLEATI_V3.2

# Install Python dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

### 1.2 Run Locally with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f cleati-api
```

**Access Points:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### 1.3 Run Tests

```bash
# Unit tests
pytest test_suite_cleati_v3.py -v

# Coverage report
pytest --cov=cleati_orchestrator_v3 --cov-report=html

# Integration tests
pytest tests/integration/ -v
```

## Phase 2: AWS Preparation

### 2.1 Setup Terraform State

```bash
# Create S3 bucket for state
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

### 2.2 Create ECR Repository

```bash
# Create private ECR repository
aws ecr create-repository \
  --repository-name cleati \
  --region eu-west-1

# Get login token
aws ecr get-login-password --region eu-west-1 | \
  docker login --username AWS --password-stdin \
  ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com
```

### 2.3 Build & Push Docker Image

```bash
# Build image
docker build -t cleati:v3.3 .

# Tag for ECR
docker tag cleati:v3.3 \
  ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/cleati:v3.3

# Push to ECR
docker push \
  ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/cleati:v3.3
```

## Phase 3: Infrastructure Deployment with Terraform

### 3.1 Initialize Terraform

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

# Format and validate
terraform fmt
terraform validate
```

### 3.2 Plan Deployment

```bash
# Review the plan
terraform plan -out=tfplan

# Expected resources (~25 resources):
# - VPC, Subnets, Security Groups
# - ALB, Target Group, Listener
# - ECS Cluster, Service, Task Definition
# - RDS PostgreSQL, DB Subnet Group
# - S3 Bucket, Bucket Policies
# - IAM Roles & Policies
# - CloudWatch Log Groups
# - Auto Scaling Policies
```

### 3.3 Apply Deployment

```bash
# Deploy infrastructure
terraform apply tfplan

# Save outputs
terraform output > outputs.txt

# Get ALB DNS (your API endpoint)
terraform output alb_dns_name
```

### 3.4 Verify Deployment

```bash
# Get ALB DNS
ALB_DNS=$(terraform output -raw alb_dns_name)

# Test health endpoint
curl http://${ALB_DNS}/api/v3/health

# Check ECS service status
aws ecs describe-services \
  --cluster cleati-v3-cluster \
  --services cleati-v3-service \
  --region eu-west-1

# View logs
aws logs tail /ecs/cleati-v3 --follow
```

## Phase 4: Monitoring & Observability

### 4.1 Setup CloudWatch Dashboards

```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name CLEATI-V3 \
  --dashboard-body file://cloudwatch-dashboard.json
```

### 4.2 Configure Alarms

```bash
# CPU utilization alarm
aws cloudwatch put-metric-alarm \
  --alarm-name cleati-cpu-high \
  --alarm-description "Alert when CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold

# Database connections alarm
aws cloudwatch put-metric-alarm \
  --alarm-name cleati-db-connections-high \
  --alarm-description "Alert when DB connections > 80" \
  --metric-name DatabaseConnections \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

### 4.3 Setup Logging

```bash
# Configure log retention
aws logs put-retention-policy \
  --log-group-name /ecs/cleati-v3 \
  --retention-in-days 30

# Create log filters for errors
aws logs put-metric-filter \
  --log-group-name /ecs/cleati-v3 \
  --filter-name ErrorCount \
  --filter-pattern "[ERROR]" \
  --metric-transformations metricName=ErrorCount,metricValue=1
```

## Phase 5: Updating & Maintenance

### 5.1 Deploy New Version

```bash
# Build new image
docker build -t cleati:v3.4 .

# Tag and push
docker tag cleati:v3.4 \
  ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/cleati:v3.4
docker push \
  ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/cleati:v3.4

# Update Terraform
terraform apply \
  -var="container_image=${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/cleati:v3.4"

# This triggers ECS service update with rolling deployment
```

### 5.2 Database Backups

```bash
# Enable automated backups (already in Terraform)
# Backups retained for 7 days

# Manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier cleati-v3-db \
  --db-snapshot-identifier cleati-v3-backup-$(date +%Y%m%d-%H%M%S)

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier cleati-v3-db-restored \
  --db-snapshot-identifier cleati-v3-backup-20231215-120000
```

### 5.3 Scaling

```bash
# Manual scaling
aws ecs update-service \
  --cluster cleati-v3-cluster \
  --service cleati-v3-service \
  --desired-count 5

# Auto-scaling is configured (3-6 tasks based on CPU/Memory)
# Metrics: CPUUtilization, MemoryUtilization
# Scale-up at: CPU 70%, Memory 80%
# Scale-down at: CPU 30%, Memory 50%
```

## Phase 6: Disaster Recovery

### 6.1 Backup Strategy

**Daily Backups:**
- RDS: Automated (7-day retention)
- S3: Versioning enabled
- Application: Container image tags

**Weekly Snapshots:**
```bash
# Weekly RDS snapshot
aws rds create-db-snapshot \
  --db-instance-identifier cleati-v3-db \
  --db-snapshot-identifier cleati-v3-weekly-$(date +%Y-W%V)
```

### 6.2 Disaster Recovery Plan

**1. Loss of AZ:**
- ALB routes traffic to healthy AZ
- RDS multi-AZ provides failover (automatic)
- Auto-scaling replaces unhealthy tasks

**2. Database Failure:**
```bash
# Restore from latest snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier cleati-v3-db-restored \
  --db-snapshot-identifier <latest-snapshot>

# Update ECS service with new DB endpoint
```

**3. Complete Service Loss:**
```bash
# Destroy and recreate
terraform destroy
terraform apply

# Restore database from snapshot during apply
```

## Phase 7: Cost Optimization

### 7.1 Current Pricing (Estimate)

**Monthly AWS Costs (eu-west-1):**
- ECS Fargate: ~€150 (3 tasks × t3.small equivalent)
- RDS PostgreSQL: ~€80 (db.t3.micro multi-AZ)
- ALB: ~€20
- Data Transfer: ~€10
- S3: ~€5
- CloudWatch: ~€5
- **Total: ~€270/month**

### 7.2 Cost Reduction Options

1. **Use Reserved Instances:** Save 30-50%
2. **Spot Instances:** Save 70% (via Fargate Spot)
3. **RDS Aurora Serverless:** Auto-scaling database
4. **Data Transfer:** CloudFront for static content
5. **Logging:** Adjust retention policies

### 7.3 Cost Monitoring

```bash
# Setup cost anomaly detection
aws ce put-anomaly-monitor \
  --anomaly-monitor '{
    "MonitorName": "CLEATI-Cost-Monitor",
    "MonitorType": "DIMENSIONAL",
    "MonitorDimension": "SERVICE"
  }'
```

## Production Checklist

```
INFRASTRUCTURE
☐ VPC, subnets, security groups configured
☐ ALB health checks passing
☐ RDS multi-AZ enabled
☐ S3 bucket encryption enabled
☐ Terraform state secured
☐ IAM roles least-privilege principle

MONITORING
☐ CloudWatch dashboards created
☐ Alarms configured (CPU, memory, database)
☐ Log retention policies set
☐ Log aggregation configured
☐ Metrics exported to CloudWatch

SECURITY
☐ SSL/TLS certificate configured
☐ Security groups restrict access
☐ RDS encryption enabled
☐ S3 versioning enabled
☐ Secrets in AWS Secrets Manager
☐ IAM audit logging enabled

DEPLOYMENT
☐ Blue-green deployment setup
☐ Rollback procedure documented
☐ Database migration strategy
☐ Load testing completed
☐ Performance baselines established

DISASTER RECOVERY
☐ Backup strategy implemented
☐ Recovery procedures documented
☐ RTO/RPO defined and tested
☐ Disaster recovery plan reviewed
```

## Support & Troubleshooting

### Common Issues

**1. ECS Tasks Failing to Start**
```bash
# Check task logs
aws ecs describe-tasks \
  --cluster cleati-v3-cluster \
  --tasks $(aws ecs list-tasks --cluster cleati-v3-cluster --query 'taskArns[0]' --output text) \
  --region eu-west-1

# View CloudWatch logs
aws logs tail /ecs/cleati-v3 --follow
```

**2. Database Connection Issues**
```bash
# Check RDS status
aws rds describe-db-instances \
  --db-instance-identifier cleati-v3-db \
  --region eu-west-1

# Test connectivity
psql -h <rds-endpoint> -U cleati_admin -d cleati
```

**3. High Memory Usage**
```bash
# Check running tasks
aws ecs describe-tasks \
  --cluster cleati-v3-cluster \
  --tasks $(aws ecs list-tasks --cluster cleati-v3-cluster --query 'taskArns' --output text) \
  --region eu-west-1

# Adjust task definition memory
terraform apply -var="container_memory=1024"
```

## Documentation

- [API Documentation](http://ALB-DNS/docs)
- [Architecture Overview](./README_V3.3.md)
- [Database Schema](./database-schema.sql)
- [API Endpoints](./API_REFERENCE.md)

## Contact & Support

For production support:
- Email: support@cleati-platform.com
- Slack: #cleati-production
- On-call: Check PagerDuty schedule

---

**Last Updated:** 2026-04-26  
**Version:** CLEATI V3.3 Production  
**Status:** Ready for Deployment
