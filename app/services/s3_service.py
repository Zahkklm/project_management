import uuid


class S3Service:
    def upload_file(self, file_content: bytes, filename: str, content_type: str):
        return f"documents/{uuid.uuid4()}/{filename}"

    def download_file(self, s3_key: str):
        return b"test content"

    def delete_file(self, s3_key: str):
        return True


s3_service = S3Service()
