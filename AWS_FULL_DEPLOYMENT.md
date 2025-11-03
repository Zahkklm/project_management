# Complete AWS Deployment Guide (Backend + Frontend)

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Users                                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────────┬──────────────────────────┐
                 │                 │                          │
                 ▼                 ▼                          ▼
┌────────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  CloudFront (Frontend) │  │ CloudFront (API) │  │   Route 53 DNS   │
│   React Static Site    │  │   HTTPS for ALB  │  │   (Optional)     │
└────────┬───────────────┘  └────────┬─────────┘  └──────────────────┘
         │                           │
         ▼                           ▼
┌────────────────────────┐  ┌──────────────────┐
│   S3 Bucket (Static)   │  │  Load Balancer   │
│   Frontend Build       │  │      (ALB)       │
└────────────────────────┘  └────────┬─────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   ECS Fargate    │
                            │  Backend Tasks   │
                            └────┬────────┬────┘
                                 │        │
                    ┌────────────┴────┐   │
                    ▼                 ▼   ▼
            ┌──────────────┐  ┌──────────────┐
            │ RDS Postgres │  │  S3 Bucket   │
            │   Database   │  │  Documents   │
            └──────────────┘  └──────┬───────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │    Lambda    │
                              │Image Processor│
                              └──────────────┘
```

## 📋 Prerequisites

1. **AWS Account** with admin access
2. **AWS CLI** installed and configured
3. **Terraform** v1.0+
4. **Node.js** 18+
5. **Docker** (for backend)
6. **Verified SES Email** for sending invitations

## 🚀 Step-by-Step Deployment

### Step 1: Verify SES Email

```bash
aws ses verify-email-identity \
  --email-address noreply@yourdomain.com \
  --region us-east-1
```

Check your email and click the verification link.

### Step 2: Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
aws_region                = "us-east-1"
environment               = "production"
s3_bucket_name            = "mycompany-project-mgmt"  # Must be globally unique
db_instance_class         = "db.t3.micro"
db_username               = "dbadmin"
db_password               = "CHANGE_THIS_SECURE_PASSWORD"
ecs_task_cpu              = "256"
ecs_task_memory           = "512"
ecs_service_desired_count = 2
ses_sender_email          = "noreply@yourdomain.com"
frontend_url              = "https://app.yourdomain.com"  # Will be updated later
```

### Step 3: Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**Save the outputs:**
```
alb_dns_name = "project-management-alb-xxxxx.us-east-1.elb.amazonaws.com"
ecr_repository_url = "123456789.dkr.ecr.us-east-1.amazonaws.com/project-management-app"
cloudfront_domain_name = "d1234567890abc.cloudfront.net"  # API
frontend_cloudfront_domain = "d0987654321xyz.cloudfront.net"  # Frontend
frontend_bucket_name = "mycompany-project-mgmt-frontend"
```

### Step 4: Build and Deploy Backend

```bash
# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <ecr_repository_url>

# Build and push
docker build -t project-management-app .
docker tag project-management-app:latest <ecr_repository_url>:latest
docker push <ecr_repository_url>:latest

# Force ECS deployment
aws ecs update-service \
  --cluster project-management-cluster \
  --service project-management-service \
  --force-new-deployment \
  --region us-east-1
```

### Step 5: Run Database Migrations

```bash
# Get RDS endpoint from Terraform output
export DATABASE_URL="postgresql://dbadmin:password@<rds-endpoint>/project_management"

# Run migrations
alembic upgrade head
```

### Step 6: Deploy Lambda Function

```bash
# Package Lambda
zip -j lambda_function.zip lambda_function.py

# Update Lambda
aws lambda update-function-code \
  --function-name project-management-image-processor \
  --zip-file fileb://lambda_function.zip \
  --region us-east-1
```

### Step 7: Build and Deploy Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build with production API URL
VITE_API_URL=https://<cloudfront_domain_name> npm run build

# Deploy to S3
aws s3 sync dist/ s3://<frontend_bucket_name>/ --delete

# Invalidate CloudFront cache
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?Origins.Items[?DomainName=='<frontend_bucket_name>.s3.amazonaws.com']].Id" \
  --output text)

aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"
```

**Or use the deployment script:**

```bash
# Linux/Mac
chmod +x deploy-frontend.sh
./deploy-frontend.sh

# Windows
deploy-frontend.bat
```

### Step 8: Update Frontend URL in Backend

Update `terraform.tfvars`:

```hcl
frontend_url = "https://<frontend_cloudfront_domain>"
```

Apply changes:

```bash
cd terraform
terraform apply
```

Force ECS redeployment to pick up new environment variable.

### Step 9: Verify Deployment

1. **Frontend**: https://\<frontend_cloudfront_domain\>
2. **API**: https://\<cloudfront_domain_name\>/docs
3. **Health Check**: https://\<cloudfront_domain_name\>/health

## 🔧 Configuration Details

### Frontend Environment Variables

The frontend needs to know the API URL. This is set during build:

```bash
VITE_API_URL=https://d1234567890abc.cloudfront.net npm run build
```

### Backend Environment Variables

Set in Terraform (`main.tf`):

```hcl
environment = [
  { name = "DATABASE_URL", value = "postgresql://..." },
  { name = "AWS_REGION", value = "us-east-1" },
  { name = "S3_BUCKET_NAME", value = "..." },
  { name = "SES_SENDER_EMAIL", value = "..." },
  { name = "FRONTEND_URL", value = "https://..." }
]
```

### CORS Configuration

Backend CORS is already configured in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For production**, update to:

```python
allow_origins=[
    "https://<frontend_cloudfront_domain>",
    "https://app.yourdomain.com"  # if using custom domain
]
```

## 🌐 Custom Domain Setup (Optional)

### For Frontend

1. **Get ACM Certificate** (us-east-1 for CloudFront):
```bash
aws acm request-certificate \
  --domain-name app.yourdomain.com \
  --validation-method DNS \
  --region us-east-1
```

2. **Add DNS validation records** in your DNS provider

3. **Update CloudFront distribution** in `terraform/frontend.tf`:
```hcl
viewer_certificate {
  acm_certificate_arn = "arn:aws:acm:us-east-1:..."
  ssl_support_method  = "sni-only"
  minimum_protocol_version = "TLSv1.2_2021"
}

aliases = ["app.yourdomain.com"]
```

4. **Create Route53 record** (or in your DNS provider):
```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "app.yourdomain.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "<frontend_cloudfront_domain>",
          "EvaluateTargetHealth": false
        }
      }
    }]
  }'
```

### For API

Similar process for `api.yourdomain.com` pointing to API CloudFront.

## 🔄 CI/CD with GitHub Actions

### Setup Secrets

Add to GitHub repository secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

### Workflows

Two workflows are provided:

1. **`.github/workflows/ci-cd.yml`** - Backend deployment
2. **`.github/workflows/deploy-frontend.yml`** - Frontend deployment

Both trigger on push to `main` branch.

## 📊 Monitoring

### CloudWatch Dashboards

Create a dashboard to monitor:

- **ECS**: CPU, Memory, Task count
- **ALB**: Request count, latency, 5xx errors
- **RDS**: Connections, CPU, storage
- **CloudFront**: Requests, error rate, cache hit ratio
- **Lambda**: Invocations, errors, duration

### CloudWatch Alarms

Set up alarms for:

```bash
# High error rate
aws cloudwatch put-metric-alarm \
  --alarm-name api-high-error-rate \
  --alarm-description "API 5xx error rate > 5%" \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold

# High CPU
aws cloudwatch put-metric-alarm \
  --alarm-name ecs-high-cpu \
  --alarm-description "ECS CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

## 💰 Cost Optimization

### Current Setup (~$95-100/month)

- ECS Fargate (2 tasks): ~$15
- RDS db.t3.micro: ~$15
- ALB: ~$20
- NAT Gateway: ~$35
- CloudFront: ~$5
- S3: ~$5
- Lambda: <$1

### Reduce Costs

1. **Use 1 ECS task** instead of 2: Save $7.50/month
2. **Remove NAT Gateway**: Save $35/month (requires public subnets for ECS)
3. **Use Aurora Serverless v2**: Pay per use instead of fixed instance
4. **Use S3 Intelligent-Tiering**: Automatic cost optimization

### Free Tier Eligible

- CloudFront: 1TB data transfer/month
- Lambda: 1M requests/month
- S3: 5GB storage, 20K GET requests
- CloudWatch: 10 custom metrics

## 🔒 Security Best Practices

### 1. Use AWS Secrets Manager

Instead of environment variables:

```bash
# Store database password
aws secretsmanager create-secret \
  --name project-management/db-password \
  --secret-string "your-secure-password"

# Update ECS task definition to reference secret
```

### 2. Enable WAF

```bash
# Create WAF WebACL
aws wafv2 create-web-acl \
  --name project-management-waf \
  --scope CLOUDFRONT \
  --default-action Allow={} \
  --rules file://waf-rules.json
```

### 3. Enable CloudTrail

```bash
aws cloudtrail create-trail \
  --name project-management-trail \
  --s3-bucket-name my-cloudtrail-bucket
```

### 4. Restrict S3 Bucket Access

Frontend bucket should only be accessible via CloudFront (already configured).

### 5. Enable VPC Flow Logs

```bash
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-xxxxx \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/project-management
```

## 🧪 Testing Deployment

### 1. Test Frontend

```bash
curl https://<frontend_cloudfront_domain>
# Should return HTML
```

### 2. Test API

```bash
# Health check
curl https://<cloudfront_domain_name>/health

# API docs
curl https://<cloudfront_domain_name>/docs
```

### 3. Test Full Flow

1. Open frontend URL in browser
2. Register a new user
3. Login
4. Create a project
5. Upload a document
6. Check S3 bucket for uploaded file
7. Check CloudWatch logs for Lambda execution (if image uploaded)

## 🔄 Updates and Rollbacks

### Update Backend

```bash
# Build new image
docker build -t project-management-app .
docker tag project-management-app:latest <ecr_repository_url>:latest
docker push <ecr_repository_url>:latest

# Deploy
aws ecs update-service \
  --cluster project-management-cluster \
  --service project-management-service \
  --force-new-deployment
```

### Update Frontend

```bash
cd frontend
npm run build
aws s3 sync dist/ s3://<frontend_bucket_name>/ --delete
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
```

### Rollback

```bash
# Backend: Deploy previous image tag
aws ecs update-service \
  --cluster project-management-cluster \
  --service project-management-service \
  --task-definition project-management-app:<previous-revision>

# Frontend: Restore from S3 versioning
aws s3api list-object-versions --bucket <frontend_bucket_name>
aws s3api copy-object --copy-source <bucket>/<key>?versionId=<id> ...
```

## 🗑️ Teardown

```bash
# Delete all resources
cd terraform
terraform destroy

# Confirm with 'yes'
```

**Warning**: This deletes everything including database and S3 buckets. Make backups first!

## 📞 Troubleshooting

### Frontend shows blank page

- Check browser console for errors
- Verify `VITE_API_URL` was set correctly during build
- Check CloudFront distribution is deployed
- Check S3 bucket has files

### API returns 502/504

- Check ECS tasks are running: `aws ecs describe-services ...`
- Check CloudWatch logs: `aws logs tail /ecs/project-management-app --follow`
- Check ALB target health: `aws elbv2 describe-target-health ...`

### CORS errors

- Update backend CORS to include frontend domain
- Redeploy backend after CORS change

### Database connection errors

- Check security group allows port 5432 from ECS
- Verify DATABASE_URL is correct
- Check RDS is in available state

## 📚 Additional Resources

- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [CloudFront Developer Guide](https://docs.aws.amazon.com/cloudfront/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## ✅ Deployment Checklist

- [ ] SES email verified
- [ ] Terraform variables configured
- [ ] Infrastructure deployed (`terraform apply`)
- [ ] Backend image built and pushed to ECR
- [ ] ECS service deployed and healthy
- [ ] Database migrations run
- [ ] Lambda function deployed
- [ ] Frontend built with correct API URL
- [ ] Frontend deployed to S3
- [ ] CloudFront cache invalidated
- [ ] Frontend accessible via CloudFront URL
- [ ] API accessible via CloudFront URL
- [ ] Test user registration and login
- [ ] Test project creation
- [ ] Test document upload
- [ ] CloudWatch alarms configured
- [ ] Backups configured

---

**Your full-stack application is now deployed to AWS!** 🎉
