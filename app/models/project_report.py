from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProjectReport(Base):
    __tablename__ = "project_report"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer, ForeignKey("projects.id"), unique=True, nullable=False
    )
    document_count = Column(Integer, default=0, nullable=False)
    total_size = Column(BigInteger, default=0, nullable=False)
    last_updated = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    project = relationship("Project", back_populates="report")
