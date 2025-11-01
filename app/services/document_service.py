from typing import Optional

from app.domain.document import (
    DocumentEntity,
    DocumentRepository,
    DocumentService,
)


class DocumentServiceImpl(DocumentService):
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    def upload_document(
        self, project_id: int, filename: str, url: str, user_id: int
    ) -> DocumentEntity:
        # Add permission checks as needed
        return self.repository.add_document(project_id, filename, url)

    def update_document(
        self, document_id: int, filename: str, url: str, user_id: int
    ) -> Optional[DocumentEntity]:
        # Add permission checks as needed
        return self.repository.update_document(document_id, filename, url)

    def delete_document(self, document_id: int, user_id: int) -> bool:
        # Add permission checks as needed
        return self.repository.delete_document(document_id)

    def get_document(
        self, document_id: int, user_id: int
    ) -> Optional[DocumentEntity]:
        # Add permission checks as needed
        return self.repository.get_document(document_id)
