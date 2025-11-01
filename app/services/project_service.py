from typing import List, Optional

from app.domain.project import (
    ProjectEntity,
    ProjectRepository,
    ProjectService,
)


class ProjectServiceImpl(ProjectService):
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(
        self, name: str, description: str, owner_id: int
    ) -> ProjectEntity:
        return self.repository.create_project(name, description, owner_id)

    def update_project(
        self, project_id: int, name: str, description: str, user_id: int
    ) -> Optional[ProjectEntity]:
        project = self.repository.get_project(project_id)
        if project and project.owner_id == user_id:
            return self.repository.update_project(
                project_id, name, description
            )
        return None

    def delete_project(self, project_id: int, user_id: int) -> bool:
        project = self.repository.get_project(project_id)
        if project and project.owner_id == user_id:
            return self.repository.delete_project(project_id)
        return False

    def get_project_info(
        self, project_id: int, user_id: int
    ) -> Optional[ProjectEntity]:
        project = self.repository.get_project(project_id)
        if project and (
            project.owner_id == user_id or user_id in project.document_ids
        ):
            return project
        return None

    def list_user_projects(self, user_id: int) -> List[ProjectEntity]:
        return self.repository.list_projects_for_user(user_id)
