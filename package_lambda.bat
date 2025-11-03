@echo off
REM Script to package Lambda function for deployment (Windows)

echo Packaging Lambda function...

REM Create temporary directory
set TEMP_DIR=lambda_package
if exist %TEMP_DIR% rmdir /s /q %TEMP_DIR%
mkdir %TEMP_DIR%

REM Copy Lambda function
copy lambda_function.py %TEMP_DIR%\

REM Install dependencies in the package directory
echo Installing dependencies...
pip install -r lambda_requirements.txt -t %TEMP_DIR%\ --platform manylinux2014_x86_64 --only-binary=:all:

REM Create zip file
echo Creating zip file...
cd %TEMP_DIR%
tar -a -c -f ..\lambda_function.zip *
cd ..

REM Cleanup
rmdir /s /q %TEMP_DIR%

echo.
echo Lambda package created: lambda_function.zip
echo.
echo Next steps:
echo 1. Run 'terraform apply' to deploy infrastructure
echo 2. Lambda will use this zip file from the project root
