import pytest

from app.domain.user import UserEntity
from app.services.user_service import UserServiceImpl


class DummyUserRepository:
    def __init__(self):
        self.users = {}
        self.counter = 1

    def get_user(self, user_id):
        return self.users.get(user_id)

    def get_user_by_login(self, login):
        for user in self.users.values():
            if user.login == login:
                return user
        return None

    def create_user(self, login, hashed_password):
        user = UserEntity(self.counter, login, hashed_password)
        self.users[self.counter] = user
        self.counter += 1
        return user


@pytest.fixture
def user_service():
    repo = DummyUserRepository()
    return UserServiceImpl(repo)


def test_register_user(user_service):
    user = user_service.register_user("test", "pass")
    assert user.login == "test"


def test_authenticate_user(user_service):
    user = user_service.register_user("test", "pass")
    assert user_service.authenticate_user("test", "pass").id == user.id
    assert user_service.authenticate_user("test", "wrong") is None
