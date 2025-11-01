import io
import os

import boto3
from PIL import Image


def lambda_handler(event, context):
    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL", "http://localhost:4566"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )
    bucket = event["bucket"]
    key = event["key"]
    size = event.get("size", (128, 128))
    response = s3.get_object(Bucket=bucket, Key=key)
    image = Image.open(io.BytesIO(response["Body"].read()))
    image = image.resize(size)
    out_buffer = io.BytesIO()
    image.save(out_buffer, format="JPEG")
    out_buffer.seek(0)
    resized_key = f"resized/{key}"
    s3.put_object(Bucket=bucket, Key=resized_key, Body=out_buffer)
    return {"resized_key": resized_key, "size": size}
