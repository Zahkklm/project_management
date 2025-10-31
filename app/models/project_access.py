from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProjectAccess(Base):
    __tablename__ = "project_accesses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="project_accesses")
    user = relationship("User", back_populates="project_accesses")

    __table_args__ = (UniqueConstraint("project_id", "user_id", name="_project_user_uc"),)
