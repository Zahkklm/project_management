# Pre-Deployment Checklist

Complete this checklist before deploying to AWS.

## ✅ Prerequisites

- [ ] AWS Account created
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Terraform installed (v1.0+)
- [ ] Docker installed
- [ ] Domain email for SES (optional but recommended)

## ✅ Step 1: Package Lambda Function

The Lambda function needs to be packaged with dependencies before Terraform can deploy it.

### Windows:
```cmd
package_lambda.bat
```

### Linux/Mac:
```bash
chmod +x package_lambda.sh
./package_lambda.sh
```

**Expected Output**: `lambda_function.zip` in project root (should be ~15-20MB with Pillow)

## ✅ Step 2: Configure Terraform Variables

1. Copy example file:
```bash
cd terraform
copy terraform.tfvars.example terraform.tfvars  # Windows
# or
cp terraform.tfvars.example terraform.tfvars    # Linux/Mac
```

2. Edit `terraform.tfvars` with your values:

**Required Variables**:
```hcl
aws_region                = "us-east-1"           # Your AWS region
environment               = "production"          # or "dev"
s3_bucket_name            = "your-unique-name"    # MUST be globally unique
db_username               = "dbadmin"             # Database username
db_password               = "CHANGE_ME_STRONG"    # STRONG password (min 8 chars)
ses_sender_email          = "noreply@yourdomain.com"  # Your verified email
frontend_url              = "http://localhost:3000"   # Your frontend URL
```

**Optional Variables** (have defaults):
```hcl
db_instance_class         = "db.t3.micro"    # RDS instance size
ecs_task_cpu              = "256"            # ECS CPU units
ecs_task_memory           = "512"            # ECS memory (MB)
ecs_service_desired_count = 2                # Number of tasks
```

⚠️ **IMPORTANT**: 
- S3 bucket names must be globally unique across ALL AWS accounts
- Use a strong database password
- Keep `terraform.tfvars` secret (it's in .gitignore)

## ✅ Step 3: Verify SES Email (Optional but Recommended)

If you want to use email invitations:

1. **Via AWS Console**:
   - Go to AWS Console → SES → Email Addresses
   - Click "Verify a New Email Address"
   - Enter your sender email
   - Check your email and click verification link

2. **Via AWS CLI**:
```bash
aws ses verify-email-identity --email-address noreply@yourdomain.com --region us-east-1
```

3. **Check verification status**:
```bash
aws ses get-identity-verification-attributes --identities noreply@yourdomain.com --region us-east-1
```

**Note**: Without verification, emails will fail. You can use `USE_MOCK_EMAIL=true` in development.

## ✅ Step 4: Initialize Terraform

```bash
cd terraform
terraform init
```

**Expected Output**:
```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.x.x...
Terraform has been successfully initialized!
```

## ✅ Step 5: Review Deployment Plan

```bash
terraform plan
```

**What to Check**:
- ✅ ~30-35 resources will be created
- ✅ VPC, subnets, security groups
- ✅ ECS cluster and service (Fargate)
- ✅ RDS PostgreSQL instance
- ✅ S3 bucket
- ✅ Lambda function
- ✅ Application Load Balancer
- ✅ IAM roles and policies

**Review carefully** - this will create billable resources!

## ✅ Step 6: Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted.

**Duration**: 10-15 minutes (RDS takes longest)

**Save these outputs**:
```
alb_dns_name = "project-management-alb-xxxxx.us-east-1.elb.amazonaws.com"
ecr_repository_url = "123456789.dkr.ecr.us-east-1.amazonaws.com/project-management-app"
database_endpoint = "project-management-db.xxxxx.us-east-1.rds.amazonaws.com:5432"
s3_bucket_name = "your-unique-bucket-name"
```

## ✅ Step 7: Run Database Migrations

After infrastructure is deployed, run migrations:

### Option A: Locally (Recommended for first deployment)
```bash
# Set DATABASE_URL from Terraform output
export DATABASE_URL="postgresql://dbadmin:yourpassword@<rds-endpoint>/project_management"

# Run migrations
alembic upgrade head
```

### Option B: From ECS Task (after first deployment)
```bash
aws ecs execute-command \
  --cluster project-management-cluster \
  --task <task-id> \
  --container app \
  --command "alembic upgrade head" \
  --interactive
```

## ✅ Step 8: Build and Push Docker Image

1. **Authenticate with ECR**:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ecr_repository_url>
```

2. **Build Docker image**:
```bash
cd ..  # back to project root
docker build -t project-management-app .
```

3. **Tag the image**:
```bash
docker tag project-management-app:latest <ecr_repository_url>:latest
```

4. **Push to ECR**:
```bash
docker push <ecr_repository_url>:latest
```

## ✅ Step 9: Update ECS Service

Force ECS to pull and deploy the new image:

```bash
aws ecs update-service \
  --cluster project-management-cluster \
  --service project-management-service \
  --force-new-deployment \
  --region us-east-1
```

## ✅ Step 10: Verify Deployment

1. **Check ECS Service Status**:
```bash
aws ecs describe-services \
  --cluster project-management-cluster \
  --services project-management-service \
  --region us-east-1
```

Look for `runningCount: 2` and `desiredCount: 2`.

2. **Test API**:
```bash
curl http://<alb_dns_name>/docs
```

You should see the FastAPI documentation page.

3. **Check Logs**:
```bash
aws logs tail /ecs/project-management-app --follow --region us-east-1
```

4. **Test Lambda**:
Upload an image to S3 and check CloudWatch logs:
```bash
aws logs tail /aws/lambda/project-management-image-processor --follow --region us-east-1
```

## ✅ Step 11: Configure GitHub Actions (Optional)

For automated deployments:

1. **Add GitHub Secrets**:
   - Go to repo Settings → Secrets and variables → Actions
   - Add:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`
     - `AWS_REGION`

2. **Push to main branch**:
```bash
git push origin main
```

GitHub Actions will automatically deploy on every push.

## 🎉 Deployment Complete!

Your API is now live at:
```
http://<alb_dns_name>
```

**Access Points**:
- API Docs: `http://<alb_dns_name>/docs`
- Health Check: `http://<alb_dns_name>/docs`

## 📊 Post-Deployment Monitoring

1. **CloudWatch Logs**:
   - ECS: `/ecs/project-management-app`
   - Lambda: `/aws/lambda/project-management-image-processor`

2. **ECS Metrics**:
   - Go to AWS Console → ECS → Clusters → project-management-cluster

3. **RDS Monitoring**:
   - Go to AWS Console → RDS → project-management-db

4. **S3 Usage**:
   - Go to AWS Console → S3 → your-bucket-name

## 🧹 Teardown (If Needed)

To destroy all infrastructure and stop billing:

```bash
cd terraform
terraform destroy
```

Type `yes` when prompted.

**Warning**: This will delete:
- Database (all data)
- S3 bucket (all files)
- All infrastructure

Make backups before destroying!

## 💰 Cost Estimate

**Monthly costs** (us-east-1):
- ECS Fargate (2 tasks): ~$30
- RDS db.t3.micro: ~$15
- ALB: ~$20
- NAT Gateway: ~$35
- S3: ~$1-5 (storage dependent)
- Lambda: ~$0-1 (usage dependent)

**Total**: ~$95-105/month

**Cost Optimization Tips**:
- Use 1 ECS task for dev: saves $15
- Use smaller RDS: db.t3.micro is already minimal
- Remove NAT Gateway for dev (use public subnets): saves $35

## 🐛 Troubleshooting

### ECS Tasks Not Starting
- Check CloudWatch logs: `aws logs tail /ecs/project-management-app --follow`
- Verify Docker image is in ECR
- Check security group allows ALB → ECS traffic

### Database Connection Errors
- Verify security group allows ECS → RDS on port 5432
- Check DATABASE_URL in task definition
- Ensure migrations ran successfully

### Lambda Not Triggering
- Verify S3 notification is configured
- Check Lambda permissions
- Upload test image to S3
- Check Lambda logs: `aws logs tail /aws/lambda/project-management-image-processor`

### Email Not Sending
- Verify SES email is verified
- Check `USE_MOCK_EMAIL=false` in task definition
- Review CloudWatch logs for SES errors

## 📚 Additional Resources

- [AWS Deployment Guide](AWS_DEPLOYMENT.md)
- [GitHub Secrets Setup](.github/SECRETS.md)
- [Project Completion Summary](PROJECT_COMPLETION.md)
- [Terraform Variables](terraform/terraform.tfvars.example)

---

**Need Help?**
- Check CloudWatch logs
- Review Terraform plan output
- Consult AWS documentation
- Open GitHub issue
