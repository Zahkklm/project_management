from abc import ABC, abstractmethod
from typing import List, Optional


class ProjectEntity:
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        owner_id: int,
        document_ids: Optional[List[int]] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.document_ids = document_ids or []


class ProjectRepository(ABC):
    @abstractmethod
    def get_project(self, project_id: int) -> Optional[ProjectEntity]:
        pass

    @abstractmethod
    def create_project(
        self, name: str, description: str, owner_id: int
    ) -> ProjectEntity:
        pass

    @abstractmethod
    def update_project(
        self, project_id: int, name: str, description: str
    ) -> Optional[ProjectEntity]:
        pass

    @abstractmethod
    def delete_project(self, project_id: int) -> bool:
        pass

    @abstractmethod
    def list_projects_for_user(self, user_id: int) -> List[ProjectEntity]:
        pass


class ProjectService(ABC):
    @abstractmethod
    def create_project(
        self, name: str, description: str, owner_id: int
    ) -> ProjectEntity:
        pass

    @abstractmethod
    def update_project(
        self, project_id: int, name: str, description: str, user_id: int
    ) -> Optional[ProjectEntity]:
        pass

    @abstractmethod
    def delete_project(self, project_id: int, user_id: int) -> bool:
        pass

    @abstractmethod
    def get_project_info(
        self, project_id: int, user_id: int
    ) -> Optional[ProjectEntity]:
        pass

    @abstractmethod
    def list_user_projects(self, user_id: int) -> List[ProjectEntity]:
        pass
