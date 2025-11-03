@echo off
setlocal enabledelayedexpansion

echo Deploying Frontend to AWS...

REM Check if AWS CLI is installed
where aws >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo AWS CLI not found. Please install it first.
    exit /b 1
)

REM Get bucket name from Terraform output
cd terraform
for /f "delims=" %%i in ('terraform output -raw frontend_bucket_name 2^>nul') do set BUCKET_NAME=%%i
cd ..

if "%BUCKET_NAME%"=="" (
    echo Frontend bucket not found. Run 'terraform apply' first.
    exit /b 1
)

echo Building frontend...
cd frontend
call npm install
call npm run build

echo Uploading to S3...
aws s3 sync dist\ s3://%BUCKET_NAME%/ --delete

echo Frontend deployed successfully!
cd ..
cd terraform
for /f "delims=" %%i in ('terraform output -raw frontend_cloudfront_domain') do set CLOUDFRONT_DOMAIN=%%i
cd ..
echo URL: https://%CLOUDFRONT_DOMAIN%

pause
