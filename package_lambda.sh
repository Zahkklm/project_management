#!/bin/bash
# Script to package Lambda function for deployment

echo "📦 Packaging Lambda function..."

# Create temporary directory
TEMP_DIR="lambda_package"
rm -rf $TEMP_DIR
mkdir -p $TEMP_DIR

# Copy Lambda function
cp lambda_function.py $TEMP_DIR/

# Install dependencies in the package directory
echo "📥 Installing dependencies..."
pip install -r lambda_requirements.txt -t $TEMP_DIR/ --platform manylinux2014_x86_64 --only-binary=:all:

# Create zip file
echo "🗜️ Creating zip file..."
cd $TEMP_DIR
zip -r ../lambda_function.zip . -q
cd ..

# Cleanup
rm -rf $TEMP_DIR

# Check file size
SIZE=$(du -h lambda_function.zip | cut -f1)
echo "✅ Lambda package created: lambda_function.zip ($SIZE)"
echo ""
echo "📍 Location: $(pwd)/lambda_function.zip"
echo ""
echo "Next steps:"
echo "1. Run 'terraform apply' to deploy infrastructure"
echo "2. Lambda will use this zip file from the project root"
