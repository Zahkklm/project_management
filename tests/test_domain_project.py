import pytest

from app.domain.project import ProjectEntity
from app.services.project_service import ProjectServiceImpl


class DummyProjectRepository:
    def __init__(self):
        self.projects = {}
        self.counter = 1

    def get_project(self, project_id):
        return self.projects.get(project_id)

    def create_project(self, name, description, owner_id):
        project = ProjectEntity(self.counter, name, description, owner_id)
        self.projects[self.counter] = project
        self.counter += 1
        return project

    def update_project(self, project_id, name, description):
        project = self.projects.get(project_id)
        if project:
            project.name = name
            project.description = description
            return project
        return None

    def delete_project(self, project_id):
        return self.projects.pop(project_id, None) is not None

    def list_projects_for_user(self, user_id):
        return [p for p in self.projects.values() if p.owner_id == user_id]


@pytest.fixture
def project_service():
    repo = DummyProjectRepository()
    return ProjectServiceImpl(repo)


def test_create_project(project_service):
    project = project_service.create_project("Test", "Desc", 1)
    assert project.name == "Test"
    assert project.owner_id == 1


def test_update_project(project_service):
    project = project_service.create_project("Test", "Desc", 1)
    updated = project_service.update_project(project.id, "New", "NewDesc", 1)
    assert updated.name == "New"


def test_delete_project(project_service):
    project = project_service.create_project("Test", "Desc", 1)
    assert project_service.delete_project(project.id, 1)
    assert not project_service.delete_project(project.id, 1)
