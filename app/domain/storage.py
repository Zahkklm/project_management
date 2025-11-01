from abc import ABC, abstractmethod
from typing import List


class S3ServiceInterface(ABC):
    @abstractmethod
    def upload_file(self, file_path: str, bucket: str, key: str) -> str:
        pass

    @abstractmethod
    def download_file(self, bucket: str, key: str) -> bytes:
        pass

    @abstractmethod
    def delete_file(self, bucket: str, key: str) -> bool:
        pass

    @abstractmethod
    def list_files(self, bucket: str, prefix: str = "") -> List[str]:
        pass
