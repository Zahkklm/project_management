import os

import boto3

from app.domain.storage import S3ServiceInterface


class S3Service(S3ServiceInterface):
    def _get_client(self):
        """
        Build an S3 client that prefers the AWS task/instance role when no explicit
        credentials are provided. Only inject access key/secret if present in env.
        This avoids breaking on ECS where IAM roles should be used.
        """
        region_name = os.environ.get("AWS_REGION", "us-east-1")
        client_kwargs = {
            "service_name": "s3",
            "region_name": region_name,
        }

        # Only pass creds if explicitly provided (and not dummy defaults)
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        if (
            aws_access_key_id
            and aws_secret_access_key
            and aws_access_key_id != "test"
            and aws_secret_access_key != "test"
        ):
            client_kwargs["aws_access_key_id"] = aws_access_key_id
            client_kwargs["aws_secret_access_key"] = aws_secret_access_key

        return boto3.client(**client_kwargs)

    def upload_file(self, file_path: str, bucket: str, key: str) -> str:  # type: ignore[override]
        s3 = self._get_client()
        with open(file_path, "rb") as f:
            s3.put_object(Bucket=bucket, Key=key, Body=f.read())
        return key

    def download_file(self, bucket: str, key: str) -> bytes:
        s3 = self._get_client()
        response = s3.get_object(Bucket=bucket, Key=key)
        body = response["Body"].read()
        if not isinstance(body, bytes):
            raise TypeError("download_file must return bytes")
        return body

    def delete_file(self, bucket: str, key: str) -> bool:
        s3 = self._get_client()
        s3.delete_object(Bucket=bucket, Key=key)
        return True

    def list_files(self, bucket: str, prefix: str = "") -> list[str]:
        s3 = self._get_client()
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return [obj["Key"] for obj in response.get("Contents", [])]
