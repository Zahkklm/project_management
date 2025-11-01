from abc import ABC, abstractmethod
from typing import Optional


class UserEntity:
    def __init__(self, id: int, login: str, hashed_password: str):
        self.id = id
        self.login = login
        self.hashed_password = hashed_password


class UserRepository(ABC):
    @abstractmethod
    def get_user(self, user_id: int) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def get_user_by_login(self, login: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def create_user(self, login: str, hashed_password: str) -> UserEntity:
        pass


class UserService(ABC):
    @abstractmethod
    def register_user(self, login: str, password: str) -> UserEntity:
        pass

    @abstractmethod
    def authenticate_user(
        self, login: str, password: str
    ) -> Optional[UserEntity]:
        pass
