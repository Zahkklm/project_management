import pytest

from app.domain.document import DocumentEntity
from app.services.document_service import DocumentServiceImpl


class DummyDocumentRepository:
    def __init__(self):
        self.documents = {}
        self.counter = 1

    def get_document(self, document_id):
        return self.documents.get(document_id)

    def add_document(self, project_id, filename, url):
        doc = DocumentEntity(self.counter, project_id, filename, url)
        self.documents[self.counter] = doc
        self.counter += 1
        return doc

    def update_document(self, document_id, filename, url):
        doc = self.documents.get(document_id)
        if doc:
            doc.filename = filename
            doc.url = url
            return doc
        return None

    def delete_document(self, document_id):
        return self.documents.pop(document_id, None) is not None


@pytest.fixture
def document_service():
    repo = DummyDocumentRepository()
    return DocumentServiceImpl(repo)


def test_upload_document(document_service):
    doc = document_service.upload_document(1, "file.pdf", "url", 1)
    assert doc.filename == "file.pdf"
    assert doc.project_id == 1


def test_update_document(document_service):
    doc = document_service.upload_document(1, "file.pdf", "url", 1)
    updated = document_service.update_document(
        doc.id, "new.pdf", "new_url", 1
    )
    assert updated.filename == "new.pdf"


def test_delete_document(document_service):
    doc = document_service.upload_document(1, "file.pdf", "url", 1)
    assert document_service.delete_document(doc.id, 1)
    assert not document_service.delete_document(doc.id, 1)
