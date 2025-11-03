# GitHub Actions Secrets Configuration

This document describes the GitHub Secrets required for the CI/CD pipeline to deploy to AWS.

## Required Secrets

Navigate to your GitHub repository → Settings → Secrets and variables → Actions, then add the following secrets:

### AWS Credentials

#### `AWS_ACCESS_KEY_ID`
- **Description**: AWS access key for deployment
- **How to get**: 
  1. Go to AWS Console → IAM → Users
  2. Create a new user or select existing user
  3. Generate access keys
  4. Copy the Access Key ID
- **Required permissions**: 
  - ECR (push images)
  - ECS (update services)
  - Lambda (update function code)

#### `AWS_SECRET_ACCESS_KEY`
- **Description**: AWS secret access key for deployment
- **How to get**: Same as above, copy the Secret Access Key
- **Security**: Never commit this to your repository

#### `AWS_REGION`
- **Description**: AWS region where resources are deployed
- **Example**: `us-east-1`
- **Default**: The region you chose in terraform.tfvars

## IAM Policy for GitHub Actions

The AWS user needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices"
      ],
      "Resource": "arn:aws:ecs:*:*:service/project-management-cluster/project-management-service"
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:GetFunction"
      ],
      "Resource": "arn:aws:lambda:*:*:function:project-management-image-processor"
    }
  ]
}
```

## Setting Up GitHub Secrets

### Via GitHub UI

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its name and value
5. Click **Add secret**

### Via GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Authenticate
gh auth login

# Add secrets
gh secret set AWS_ACCESS_KEY_ID
# Paste your access key when prompted

gh secret set AWS_SECRET_ACCESS_KEY
# Paste your secret key when prompted

gh secret set AWS_REGION
# Enter your region when prompted
```

## Verification

After adding secrets, you can verify they're set (values are hidden):

```bash
gh secret list
```

Expected output:
```
AWS_ACCESS_KEY_ID       Updated 2024-01-01
AWS_SECRET_ACCESS_KEY   Updated 2024-01-01
AWS_REGION              Updated 2024-01-01
```

## Security Best Practices

1. **Rotate Credentials**: Rotate AWS access keys every 90 days
2. **Least Privilege**: Only grant permissions needed for deployment
3. **Audit**: Monitor AWS CloudTrail for API calls
4. **Use IAM Roles**: For production, consider using OIDC with GitHub Actions
5. **Separate Environments**: Use different credentials for staging and production

## Testing the Pipeline

After setting up secrets:

1. Push a commit to the `main` branch
2. Go to **Actions** tab in GitHub
3. Watch the CI/CD pipeline run
4. Verify deploy job succeeds

If deployment fails, check:
- Secrets are correctly set
- IAM permissions are sufficient
- AWS resources exist (created by Terraform)
- ECS cluster and service names match

## Using OIDC (Recommended for Production)

Instead of long-lived access keys, use OpenID Connect:

1. Create an IAM OIDC provider for GitHub
2. Create an IAM role with trust policy for GitHub
3. Update workflow to use `aws-actions/configure-aws-credentials@v4` with role-arn

See: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services
