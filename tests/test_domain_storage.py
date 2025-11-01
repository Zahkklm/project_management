import pytest

from app.domain.storage import S3ServiceInterface


class DummyS3Service(S3ServiceInterface):
    def upload_file(self, file_path, bucket, key):
        return f"s3://{bucket}/{key}"

    def download_file(self, bucket, key):
        return b"content"

    def delete_file(self, bucket, key):
        return True

    def list_files(self, bucket, prefix=""):
        return [f"{prefix}file1", f"{prefix}file2"]


@pytest.fixture
def s3_service():
    return DummyS3Service()


def test_upload_file(s3_service):
    url = s3_service.upload_file("path", "bucket", "key")
    assert url == "s3://bucket/key"


def test_download_file(s3_service):
    content = s3_service.download_file("bucket", "key")
    assert content == b"content"


def test_delete_file(s3_service):
    assert s3_service.delete_file("bucket", "key")


def test_list_files(s3_service):
    files = s3_service.list_files("bucket", "prefix/")
    assert files == ["prefix/file1", "prefix/file2"]
