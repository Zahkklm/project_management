from abc import ABC, abstractmethod
from typing import Optional


class DocumentEntity:
    def __init__(self, id: int, project_id: int, filename: str, url: str):
        self.id = id
        self.project_id = project_id
        self.filename = filename
        self.url = url


class DocumentRepository(ABC):
    @abstractmethod
    def get_document(self, document_id: int) -> Optional[DocumentEntity]:
        pass

    @abstractmethod
    def add_document(
        self, project_id: int, filename: str, url: str
    ) -> DocumentEntity:
        pass

    @abstractmethod
    def update_document(
        self, document_id: int, filename: str, url: str
    ) -> Optional[DocumentEntity]:
        pass

    @abstractmethod
    def delete_document(self, document_id: int) -> bool:
        pass


class DocumentService(ABC):
    @abstractmethod
    def upload_document(
        self, project_id: int, filename: str, url: str, user_id: int
    ) -> DocumentEntity:
        pass

    @abstractmethod
    def update_document(
        self, document_id: int, filename: str, url: str, user_id: int
    ) -> Optional[DocumentEntity]:
        pass

    @abstractmethod
    def delete_document(self, document_id: int, user_id: int) -> bool:
        pass

    @abstractmethod
    def get_document(
        self, document_id: int, user_id: int
    ) -> Optional[DocumentEntity]:
        pass
