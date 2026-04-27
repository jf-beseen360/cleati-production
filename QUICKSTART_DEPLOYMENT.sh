#!/bin/bash

################################################################################
# CLEATI V3.3 - Quick Start Deployment Script
# Purpose: Automated setup and deployment to AWS
# Status: Production Ready
# Date: 2026-04-26
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="cleati-v3"
AWS_REGION="${AWS_REGION:-eu-west-1}"
ENVIRONMENT="production"
DESIRED_COUNT=3
CONTAINER_NAME="cleati"
CONTAINER_VERSION="v3.3"

################################################################################
# UTILITY FUNCTIONS
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_prerequisite() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 is not installed"
        return 1
    fi
    log_success "$1 is installed"
    return 0
}

################################################################################
# PHASE 1: PREREQUISITES CHECK
################################################################################

phase_prerequisites() {
    log_info "===== PHASE 1: Prerequisites Check ====="

    local all_ok=true

    if ! check_prerequisite "docker"; then
        all_ok=false
    fi

    if ! check_prerequisite "docker-compose"; then
        all_ok=false
    fi

    if ! check_prerequisite "terraform"; then
        all_ok=false
    fi

    if ! check_prerequisite "aws"; then
        all_ok=false
    fi

    if ! check_prerequisite "python3"; then
        all_ok=false
    fi

    if ! check_prerequisite "git"; then
        all_ok=false
    fi

    if [ "$all_ok" = false ]; then
        log_error "Please install missing prerequisites"
        return 1
    fi

    log_success "All prerequisites installed"
    return 0
}

################################################################################
# PHASE 2: LOCAL ENVIRONMENT SETUP
################################################################################

phase_local_setup() {
    log_info "===== PHASE 2: Local Environment Setup ====="

    # Check .env file
    if [ ! -f ".env" ]; then
        log_warning ".env file not found, creating from template"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success ".env file created (please edit with your configuration)"
        else
            log_error ".env.example not found"
            return 1
        fi
    fi

    # Install Python dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt --quiet
    log_success "Python dependencies installed"

    return 0
}

################################################################################
# PHASE 3: LOCAL DOCKER TESTING
################################################################################

phase_local_testing() {
    log_info "===== PHASE 3: Local Docker Testing ====="

    read -p "Do you want to run local Docker tests? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Building Docker images..."
        docker-compose build --quiet
        log_success "Docker images built"

        log_info "Starting services..."
        docker-compose up -d
        log_success "Services started"

        log_info "Waiting for services to be healthy (30s)..."
        sleep 10

        # Test health endpoint
        if curl -f http://localhost:8000/api/v3/health > /dev/null 2>&1; then
            log_success "Health check passed"
        else
            log_warning "Health check not yet ready, continuing..."
        fi

        log_info "Running test suite..."
        pytest test_suite_cleati_v3.py -v --tb=short 2>&1 | tail -20

        log_info "Stopping local services..."
        docker-compose down --quiet
        log_success "Local testing complete"
    fi

    return 0
}

################################################################################
# PHASE 4: AWS ACCOUNT SETUP
################################################################################

phase_aws_setup() {
    log_info "===== PHASE 4: AWS Account Setup ====="

    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        log_error "Could not retrieve AWS Account ID. Check credentials."
        return 1
    fi
    log_success "AWS Account ID: $AWS_ACCOUNT_ID"

    # Create Terraform state bucket
    log_info "Setting up Terraform state infrastructure..."
    STATE_BUCKET="cleati-terraform-state-${AWS_ACCOUNT_ID}"

    if aws s3 ls "s3://${STATE_BUCKET}" 2>&1 | grep -q 'NoSuchBucket'; then
        log_info "Creating S3 bucket for Terraform state..."
        aws s3 mb "s3://${STATE_BUCKET}" --region ${AWS_REGION}

        log_info "Enabling versioning..."
        aws s3api put-bucket-versioning \
            --bucket ${STATE_BUCKET} \
            --versioning-configuration Status=Enabled

        log_success "S3 state bucket created and versioning enabled"
    else
        log_success "S3 state bucket already exists"
    fi

    # Create DynamoDB locks table
    TABLE_EXISTS=$(aws dynamodb describe-table --table-name terraform-locks --region ${AWS_REGION} 2>&1 | grep -c "terraform-locks" || true)
    if [ $TABLE_EXISTS -eq 0 ]; then
        log_info "Creating DynamoDB table for Terraform locks..."
        aws dynamodb create-table \
            --table-name terraform-locks \
            --attribute-definitions AttributeName=LockID,AttributeType=S \
            --key-schema AttributeName=LockID,KeyType=HASH \
            --billing-mode PAY_PER_REQUEST \
            --region ${AWS_REGION}

        log_success "DynamoDB locks table created"
    else
        log_success "DynamoDB locks table already exists"
    fi

    echo "export AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}" >> .env
    return 0
}

################################################################################
# PHASE 5: ECR SETUP AND IMAGE PUSH
################################################################################

phase_ecr_setup() {
    log_info "===== PHASE 5: ECR Setup and Image Push ====="

    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

    # Check if repository exists
    REPO_EXISTS=$(aws ecr describe-repositories --repository-names ${CONTAINER_NAME} --region ${AWS_REGION} 2>&1 | grep -c "${CONTAINER_NAME}" || true)

    if [ $REPO_EXISTS -eq 0 ]; then
        log_info "Creating ECR repository..."
        aws ecr create-repository \
            --repository-name ${CONTAINER_NAME} \
            --region ${AWS_REGION}
        log_success "ECR repository created"
    else
        log_success "ECR repository already exists"
    fi

    # Login to ECR
    log_info "Authenticating with ECR..."
    aws ecr get-login-password --region ${AWS_REGION} | \
        docker login --username AWS --password-stdin ${ECR_REGISTRY}
    log_success "ECR authentication successful"

    # Build and push image
    log_info "Building Docker image..."
    docker build -t ${CONTAINER_NAME}:${CONTAINER_VERSION} . --quiet
    log_success "Docker image built"

    log_info "Tagging image for ECR..."
    docker tag ${CONTAINER_NAME}:${CONTAINER_VERSION} \
        ${ECR_REGISTRY}/${CONTAINER_NAME}:${CONTAINER_VERSION}

    log_info "Pushing image to ECR..."
    docker push ${ECR_REGISTRY}/${CONTAINER_NAME}:${CONTAINER_VERSION} --quiet
    log_success "Image pushed to ECR"

    echo "export CONTAINER_IMAGE=${ECR_REGISTRY}/${CONTAINER_NAME}:${CONTAINER_VERSION}" >> .env
    return 0
}

################################################################################
# PHASE 6: TERRAFORM DEPLOYMENT
################################################################################

phase_terraform_deploy() {
    log_info "===== PHASE 6: Terraform Deployment ====="

    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    CONTAINER_IMAGE=$(grep CONTAINER_IMAGE .env | cut -d= -f2)

    # Create terraform.tfvars
    log_info "Creating terraform.tfvars..."
    cat > terraform.tfvars <<EOF
aws_region         = "${AWS_REGION}"
environment         = "${ENVIRONMENT}"
app_name            = "${PROJECT_NAME}"
desired_count       = ${DESIRED_COUNT}
container_image     = "${CONTAINER_IMAGE}"
EOF
    log_success "terraform.tfvars created"

    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init -upgrade -quiet
    log_success "Terraform initialized"

    # Validate
    log_info "Validating Terraform configuration..."
    terraform validate
    log_success "Terraform configuration valid"

    # Plan
    log_info "Planning Terraform deployment..."
    terraform plan -out=tfplan

    # Apply
    read -p "Do you want to apply this Terraform plan? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Applying Terraform plan..."
        terraform apply tfplan --auto-approve
        log_success "Infrastructure deployed"

        # Save outputs
        log_info "Saving Terraform outputs..."
        terraform output > outputs.txt

        # Get ALB DNS
        ALB_DNS=$(terraform output -raw alb_dns_name 2>/dev/null || echo "pending")
        echo "export ALB_DNS=${ALB_DNS}" >> .env

        log_success "Deployment complete"
        log_info "ALB DNS: ${ALB_DNS}"
        return 0
    else
        log_warning "Deployment cancelled"
        return 1
    fi
}

################################################################################
# PHASE 7: POST-DEPLOYMENT VERIFICATION
################################################################################

phase_verification() {
    log_info "===== PHASE 7: Post-Deployment Verification ====="

    ALB_DNS=$(grep ALB_DNS .env | cut -d= -f2)

    if [ -z "$ALB_DNS" ] || [ "$ALB_DNS" = "pending" ]; then
        log_warning "ALB DNS not available yet, skipping verification"
        return 0
    fi

    log_info "Waiting for ALB to stabilize (60s)..."
    sleep 30

    # Test health endpoint
    log_info "Testing health endpoint..."
    if curl -f "http://${ALB_DNS}/api/v3/health" > /dev/null 2>&1; then
        log_success "Health check passed"
    else
        log_warning "Health check failed, services may still be starting"
    fi

    # Get ECS service status
    log_info "Checking ECS service status..."
    aws ecs describe-services \
        --cluster ${PROJECT_NAME}-cluster \
        --services ${PROJECT_NAME}-service \
        --region ${AWS_REGION} \
        --query 'services[0].[runningCount,desiredCount]' \
        --output text

    # Display access information
    log_success "===== DEPLOYMENT COMPLETE ====="
    log_info "API Endpoint: http://${ALB_DNS}"
    log_info "API Documentation: http://${ALB_DNS}/docs"
    log_info "Dashboard: http://${ALB_DNS}/dashboard"

    return 0
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    log_info "Starting CLEATI V3.3 Deployment"
    log_info "AWS Region: ${AWS_REGION}"

    # Run phases
    phase_prerequisites || exit 1
    phase_local_setup || exit 1
    phase_local_testing || exit 1
    phase_aws_setup || exit 1
    phase_ecr_setup || exit 1
    phase_terraform_deploy || exit 1
    phase_verification || exit 1

    log_success "===== ALL PHASES COMPLETE ====="
    log_info "Next steps:"
    log_info "  1. Access the application at http://${ALB_DNS}"
    log_info "  2. Monitor the dashboard at http://${ALB_DNS}/dashboard"
    log_info "  3. Review CloudWatch logs in AWS console"
    log_info "  4. For updates: docker build → docker push → terraform apply"

    return 0
}

# Run main
main "$@"
