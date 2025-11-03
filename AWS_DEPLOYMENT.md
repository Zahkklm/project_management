# AWS Deployment Guide

This guide walks you through deploying the Project Management API to AWS using Terraform and GitHub Actions.

## Architecture

The application is deployed using the following AWS services:

- **ECS Fargate**: Serverless container orchestration for the FastAPI application
- **Application Load Balancer**: Distributes traffic across ECS tasks
- **RDS PostgreSQL**: Managed database service
- **S3**: Document storage with versioning
- **Lambda**: Image processing functions triggered by S3 events
- **SES**: Email service for project invitations
- **ECR**: Docker container registry
- **CloudWatch**: Logging and monitoring
- **VPC**: Isolated network with public and private subnets
- **NAT Gateway**: Allows private subnets to access the internet

## Prerequisites

1. **AWS Account**: Active AWS account with appropriate permissions
2. **AWS CLI**: Installed and configured with credentials
3. **Terraform**: Version 1.0 or later
4. **Docker**: For building container images
5. **Domain Email**: For SES sender verification

## Step 1: Verify SES Email

Before deployment, you must verify your sender email address in AWS SES:

```bash
# Verify email via AWS Console
# Go to AWS Console → SES → Email Addresses → Verify a New Email Address
# Or use AWS CLI:
aws ses verify-email-identity --email-address noreply@yourdomain.com --region us-east-1
```

Check your email and click the verification link. Wait for verification to complete.

## Step 2: Configure Terraform Variables

1. Copy the example variables file:
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` with your values:
```hcl
aws_region                = "us-east-1"
environment               = "production"
s3_bucket_name            = "your-unique-bucket-name"
db_instance_class         = "db.t3.micro"
db_username               = "dbadmin"
db_password               = "YOUR_SECURE_PASSWORD_HERE"
ecs_task_cpu              = "256"
ecs_task_memory           = "512"
ecs_service_desired_count = 2
ses_sender_email          = "noreply@yourdomain.com"
frontend_url              = "https://app.yourdomain.com"
```

**Important**: 
- S3 bucket names must be globally unique
- Use a strong database password
- Keep terraform.tfvars secure and never commit it to git

## Step 3: Initialize Terraform

```bash
cd terraform
terraform init
```

## Step 4: Plan Deployment

Review what Terraform will create:

```bash
terraform plan
```

This shows all resources that will be created. Review carefully.

## Step 5: Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted. This will take 10-15 minutes as it creates:
- VPC with subnets, NAT gateway, route tables
- Security groups
- RDS database
- S3 bucket
- ECR repository
- ECS cluster
- Application Load Balancer
- IAM roles and policies

**Save the outputs** - you'll need them:
```
alb_dns_name = "project-management-alb-xxxxx.us-east-1.elb.amazonaws.com"
ecr_repository_url = "123456789.dkr.ecr.us-east-1.amazonaws.com/project-management-app"
```

## Step 6: Run Database Migrations

After infrastructure is created, you need to run Alembic migrations:

```bash
# SSH into an ECS task or run locally with DATABASE_URL
export DATABASE_URL="postgresql://dbadmin:password@<rds-endpoint>/project_management"
alembic upgrade head
```

## Step 7: Build and Push Docker Image

1. Authenticate with ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ecr_repository_url>
```

2. Build the Docker image:
```bash
cd ..  # back to project root
docker build -t project-management-app .
```

3. Tag the image:
```bash
docker tag project-management-app:latest <ecr_repository_url>:latest
```

4. Push to ECR:
```bash
docker push <ecr_repository_url>:latest
```

## Step 8: Deploy to ECS

After pushing the image, ECS will automatically pull and deploy it:

```bash
# Force new deployment
aws ecs update-service \
  --cluster project-management-cluster \
  --service project-management-service \
  --force-new-deployment \
  --region us-east-1
```

## Step 9: Package and Deploy Lambda

```bash
# Create Lambda deployment package
cd lambda
zip -r ../lambda_function.zip lambda_function.py
cd ..

# Update Lambda function
cd terraform
terraform apply -target=aws_lambda_function.image_processor
```

## Step 10: Verify Deployment

1. **Check ECS Service**:
```bash
aws ecs describe-services \
  --cluster project-management-cluster \
  --services project-management-service \
  --region us-east-1
```

2. **Check Load Balancer**:
Visit `http://<alb_dns_name>/docs` in your browser to see the API documentation.

3. **Check Logs**:
```bash
aws logs tail /ecs/project-management-app --follow --region us-east-1
```

## Step 11: Configure DNS (Optional)

Point your domain to the ALB:

1. Get ALB DNS name from Terraform outputs
2. Create a CNAME record in your DNS provider:
   - Name: `api.yourdomain.com`
   - Value: `<alb_dns_name>`

3. For HTTPS, configure an ACM certificate and update the ALB listener.

## GitHub Actions CI/CD

The GitHub Actions workflow in `.github/workflows/ci-cd.yml` includes a deploy stage. To enable it:

1. Add AWS credentials as GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`

2. Update the deploy job in the workflow to use your ECR repository.

3. Push to the `main` branch to trigger deployment.

## Monitoring

- **CloudWatch Logs**: `/ecs/project-management-app`
- **ECS Service Metrics**: CPU, Memory, Task count
- **ALB Metrics**: Request count, latency, error rates
- **RDS Metrics**: Connections, CPU, storage

## Costs Estimate

Monthly cost for minimal production setup (us-east-1):

- ECS Fargate (2 tasks, 256 CPU, 512 MB): ~$15/month
- RDS db.t3.micro: ~$15/month
- ALB: ~$20/month
- NAT Gateway: ~$35/month
- S3: Variable, typically <$5/month
- Lambda: Pay per invocation, typically <$1/month
- CloudWatch Logs: <$5/month

**Total: ~$95-100/month**

To reduce costs:
- Use 1 ECS task instead of 2
- Use smaller RDS instance
- Remove NAT Gateway (requires public subnets for ECS)

## Teardown

To destroy all infrastructure:

```bash
cd terraform
terraform destroy
```

Type `yes` when prompted. This will delete all resources and stop billing.

**Warning**: This deletes the database and S3 bucket. Make backups first!

## Troubleshooting

### ECS Tasks Keep Restarting

Check CloudWatch logs for errors:
```bash
aws logs tail /ecs/project-management-app --follow
```

Common issues:
- Database connection failures (check security groups)
- Missing environment variables
- Image pull failures (check ECR permissions)

### Database Connection Errors

Verify:
- Security group allows port 5432 from ECS security group
- Database endpoint is correct in task definition
- Database credentials are correct

### Email Not Sending

Verify:
- SES email is verified
- IAM role has SES permissions
- Check CloudWatch logs for errors

### Lambda Not Processing Images

Check:
- S3 notification is configured
- Lambda has permissions to access S3
- CloudWatch logs for Lambda errors

## Security Considerations

1. **Secrets Management**: Use AWS Secrets Manager for production
2. **Database Credentials**: Rotate regularly
3. **IAM Policies**: Follow principle of least privilege
4. **VPC Security**: Use private subnets for sensitive resources
5. **HTTPS**: Configure ACM certificate for production
6. **WAF**: Consider AWS WAF for DDoS protection

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review Terraform plan output
3. Consult AWS documentation
4. Check GitHub Issues

## Next Steps

- Configure custom domain with Route53
- Set up HTTPS with ACM certificate
- Implement AWS Secrets Manager
- Configure backup policies for RDS
- Set up CloudWatch alarms
- Implement auto-scaling policies
