from typing import Optional

from app.domain.user import UserEntity, UserRepository, UserService


class UserServiceImpl(UserService):
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_user(self, login: str, password: str) -> UserEntity:
        # Hash password and create user
        hashed_password = password  # Replace with actual hash logic
        return self.repository.create_user(login, hashed_password)

    def authenticate_user(
        self, login: str, password: str
    ) -> Optional[UserEntity]:
        user = self.repository.get_user_by_login(login)
        if (
            user and user.hashed_password == password
        ):  # Replace with actual hash check
            return user
        return None
