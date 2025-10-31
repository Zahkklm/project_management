from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owned_projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    project_accesses = relationship(
        "ProjectAccess", back_populates="user", cascade="all, delete-orphan"
    )
