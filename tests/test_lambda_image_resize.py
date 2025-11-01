import io
import os

import boto3
from PIL import Image

from app.services.lambda_image_resize import lambda_handler


def test_lambda_image_resize(tmp_path):
    # Setup LocalStack S3
    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL", "http://localhost:4566"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )
    bucket = "test-bucket"
    s3.create_bucket(Bucket=bucket)
    # Create a test image
    img = Image.new("RGB", (256, 256), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    key = "test.jpg"
    s3.put_object(Bucket=bucket, Key=key, Body=buf)
    # Call lambda handler
    event = {"bucket": bucket, "key": key, "size": (128, 128)}
    result = lambda_handler(event, None)
    # Download resized image
    resized_obj = s3.get_object(Bucket=bucket, Key=result["resized_key"])
    resized_img = Image.open(io.BytesIO(resized_obj["Body"].read()))
    assert resized_img.size == (128, 128)
