import boto3
import json
from PIL import Image
import io

s3_client = boto3.client('s3')


def lambda_handler(event, context):
    """
    AWS Lambda function for S3 event processing:
    1. Resize images when uploaded
    2. Calculate total project file sizes
    """
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        size = record['s3']['object']['size']
        
        # Check if it's an image
        if key.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            try:
                resize_image(bucket, key)
            except Exception as e:
                print(f"Error resizing image {key}: {str(e)}")
        
        # Calculate project size
        try:
            calculate_project_size(bucket, key)
        except Exception as e:
            print(f"Error calculating project size: {str(e)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }


def resize_image(bucket, key):
    """Resize image to max 800x800 pixels"""
    response = s3_client.get_object(Bucket=bucket, Key=key)
    image_content = response['Body'].read()
    
    image = Image.open(io.BytesIO(image_content))
    
    # Resize if larger than 800x800
    if image.width > 800 or image.height > 800:
        image.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        image_format = image.format or 'JPEG'
        image.save(buffer, format=image_format)
        buffer.seek(0)
        
        # Upload resized image
        resized_key = f"resized/{key}"
        s3_client.put_object(
            Bucket=bucket,
            Key=resized_key,
            Body=buffer,
            ContentType=response['ContentType']
        )
        print(f"Resized image uploaded: {resized_key}")


def calculate_project_size(bucket, key):
    """Calculate total size of all files in a project"""
    # Extract project ID from key (assuming format: documents/{uuid}/{filename})
    parts = key.split('/')
    if len(parts) >= 2 and parts[0] == 'documents':
        project_prefix = f"{parts[0]}/{parts[1]}/"
        
        total_size = 0
        paginator = s3_client.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=bucket, Prefix=project_prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    total_size += obj['Size']
        
        # Store size in S3 metadata or DynamoDB
        size_mb = total_size / (1024 * 1024)
        print(f"Project {parts[1]} total size: {size_mb:.2f} MB")
        
        # Optional: Check size limit (e.g., 100 MB)
        MAX_SIZE_MB = 100
        if size_mb > MAX_SIZE_MB:
            print(f"WARNING: Project {parts[1]} exceeds size limit!")
            # Could trigger notification or prevent further uploads
        
        return total_size
    
    return 0
