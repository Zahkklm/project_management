#!/bin/bash
set -e

# Frontend deployment script for AWS S3 + CloudFront

echo "🚀 Deploying Frontend to AWS..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

# Get bucket name from Terraform output
BUCKET_NAME=$(cd terraform && terraform output -raw frontend_bucket_name 2>/dev/null)
CLOUDFRONT_ID=$(cd terraform && terraform output -json | jq -r '.frontend_cloudfront_domain.value' | cut -d'.' -f1)

if [ -z "$BUCKET_NAME" ]; then
    echo "❌ Frontend bucket not found. Run 'terraform apply' first."
    exit 1
fi

echo "📦 Building frontend..."
cd frontend
npm install
VITE_API_URL="https://$(cd ../terraform && terraform output -raw cloudfront_domain_name)" npm run build

echo "📤 Uploading to S3..."
aws s3 sync dist/ s3://$BUCKET_NAME/ --delete

echo "🔄 Invalidating CloudFront cache..."
if [ ! -z "$CLOUDFRONT_ID" ]; then
    aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"
fi

echo "✅ Frontend deployed successfully!"
echo "🌐 URL: https://$(cd ../terraform && terraform output -raw frontend_cloudfront_domain)"
