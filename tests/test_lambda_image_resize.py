import io
import boto3
from PIL import Image
from moto import mock_s3
from app.services.lambda_image_resize import lambda_handler


@mock_s3
def test_lambda_image_resize(tmp_path):
    s3 = boto3.client(
        "s3",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
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
