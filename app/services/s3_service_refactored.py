import os

import boto3

from app.domain.storage import S3ServiceInterface


class S3Service(S3ServiceInterface):
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv(
                "S3_ENDPOINT_URL", "http://localhost:4566"
            ),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )

    def upload_file(self, file_path: str, bucket: str, key: str) -> str:
        self.s3.upload_file(file_path, bucket, key)
        return f"s3://{bucket}/{key}"

    def download_file(self, bucket: str, key: str) -> bytes:
        response = self.s3.get_object(Bucket=bucket, Key=key)
        body = response["Body"].read()
        if not isinstance(body, bytes):
            raise TypeError("download_file must return bytes")
        return body

    def delete_file(self, bucket: str, key: str) -> bool:
        self.s3.delete_object(Bucket=bucket, Key=key)
        return True

    def list_files(self, bucket: str, prefix: str = "") -> list[str]:
        response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return [obj["Key"] for obj in response.get("Contents", [])]
