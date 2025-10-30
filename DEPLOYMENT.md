# Deployment Guide

## AWS Infrastructure Setup

### Prerequisites

- AWS CLI configured
- Terraform installed
- Docker installed
- GitHub account with repository

### 1. AWS S3 and Lambda Setup

#### Using Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
aws_region = "us-east-1"
environment = "production"
s3_bucket_name = "your-unique-bucket-name"
db_username = "admin"
db_password = "your-secure-password"
EOF

# Plan and apply
terraform plan
terraform apply
```

#### Manual Lambda Deployment

```bash
# Package Lambda function
cd ..
pip install -r lambda_requirements.txt -t lambda_package/
cp lambda_function.py lambda_package/
cd lambda_package
zip -r ../lambda_function.zip .
cd ..

# Upload to AWS Lambda
aws lambda create-function \
  --function-name project-management-processor \
  --runtime python3.10 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_function.zip \
  --timeout 60 \
  --memory-size 512
```

### 2. Database Setup

#### RDS PostgreSQL

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier project-management-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username admin \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20 \
  --storage-encrypted

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier project-management-db \
  --query 'DBInstances[0].Endpoint.Address'
```

### 3. Container Registry

#### GitHub Container Registry

```bash
# Build and tag image
docker build -t ghcr.io/YOUR_USERNAME/project-management:latest .

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Push image
docker push ghcr.io/YOUR_USERNAME/project-management:latest
```

### 4. Deployment Options

#### Option A: AWS ECS (Fargate)

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name project-management

# Create task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster project-management \
  --service-name api-service \
  --task-definition project-management-api \
  --desired-count 2 \
  --launch-type FARGATE
```

#### Option B: AWS EC2

```bash
# SSH to EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start

# Pull and run container
docker pull ghcr.io/YOUR_USERNAME/project-management:latest
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e SECRET_KEY="..." \
  -e AWS_ACCESS_KEY_ID="..." \
  -e AWS_SECRET_ACCESS_KEY="..." \
  -e S3_BUCKET_NAME="..." \
  ghcr.io/YOUR_USERNAME/project-management:latest
```

#### Option C: Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### 5. Environment Variables

Set these in your deployment environment:

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

### 6. Database Migration

```bash
# Run migrations on deployment
docker exec -it container_name alembic upgrade head
```

### 7. GitHub Actions Secrets

Add these secrets to your GitHub repository:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DATABASE_URL`
- `SECRET_KEY`
- `S3_BUCKET_NAME`

### 8. Monitoring and Logging

#### CloudWatch Logs

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/project-management

# View logs
aws logs tail /ecs/project-management --follow
```

#### Application Monitoring

Consider adding:
- AWS CloudWatch for metrics
- Sentry for error tracking
- DataDog or New Relic for APM

### 9. SSL/TLS Certificate

```bash
# Request certificate from ACM
aws acm request-certificate \
  --domain-name api.yourdomain.com \
  --validation-method DNS
```

### 10. Load Balancer Setup

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name project-management-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx

# Create target group
aws elbv2 create-target-group \
  --name project-management-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --health-check-path /health
```

## CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **On Pull Request**: Runs linting and tests
2. **On Push to main**: 
   - Runs linting and tests
   - Builds Docker image
   - Pushes to GitHub Container Registry
   - Deploys to production (if configured)

## Rollback Procedure

```bash
# List previous images
docker images ghcr.io/YOUR_USERNAME/project-management

# Deploy previous version
docker pull ghcr.io/YOUR_USERNAME/project-management:previous-tag
docker stop current-container
docker run -d ... ghcr.io/YOUR_USERNAME/project-management:previous-tag
```

## Health Checks

- Application: `GET /health`
- Database: Check RDS metrics in CloudWatch
- S3: Check bucket metrics

## Scaling

### Horizontal Scaling (ECS)

```bash
aws ecs update-service \
  --cluster project-management \
  --service api-service \
  --desired-count 5
```

### Vertical Scaling (RDS)

```bash
aws rds modify-db-instance \
  --db-instance-identifier project-management-db \
  --db-instance-class db.t3.small \
  --apply-immediately
```

## Backup Strategy

- **Database**: Automated RDS snapshots (daily)
- **S3**: Versioning enabled
- **Application**: Docker images in registry

## Security Checklist

- [ ] Enable VPC for RDS
- [ ] Use security groups to restrict access
- [ ] Enable S3 bucket encryption
- [ ] Rotate secrets regularly
- [ ] Enable CloudTrail for audit logs
- [ ] Use IAM roles instead of access keys where possible
- [ ] Enable MFA for AWS console access
- [ ] Regular security updates for dependencies
