from app.domain.document import DocumentRepository
from app.domain.project import ProjectRepository
from app.domain.user import UserRepository
from app.services.document_service import DocumentServiceImpl
from app.services.project_service import ProjectServiceImpl
from app.services.s3_service_refactored import S3Service
from app.services.user_service import UserServiceImpl

document_repository = None  # Replace with actual repository


class DummyProjectRepository(ProjectRepository):
    def get_project(self, project_id):
        return None

    def create_project(self, name, description, owner_id):
        return None

    def update_project(self, project_id, name, description):
        return None

    def delete_project(self, project_id):
        return False

    def list_projects_for_user(self, user_id):
        return []


class DummyDocumentRepository(DocumentRepository):
    def get_document(self, document_id):
        return None

    def add_document(self, project_id, filename, url):
        return None

    def update_document(self, document_id, filename, url):
        return None

    def delete_document(self, document_id):
        return False


class DummyUserRepository(UserRepository):
    def get_user(self, user_id):
        return None

    def get_user_by_login(self, login):
        return None

    def create_user(self, login, hashed_password):
        return None


project_repository = DummyProjectRepository()
project_service = ProjectServiceImpl(project_repository)

document_repository = DummyDocumentRepository()
document_service = DocumentServiceImpl(document_repository)

user_repository = DummyUserRepository()
user_service = UserServiceImpl(user_repository)

s3_service = S3Service()

# These can now be injected into API routes or other services
