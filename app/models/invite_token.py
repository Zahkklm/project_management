"""
Database model for storing project invitation tokens.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class InviteToken(Base):
    """Model for storing project invitation tokens."""

    __tablename__ = "invite_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="invite_tokens")

    @classmethod
    def create_token(
        cls, token: str, project_id: int, email: str, days_valid: int = 7
    ):
        """
        Factory method to create a new invite token.

        Args:
            token: Unique token string
            project_id: ID of the project
            email: Email address of invitee
            days_valid: Number of days the token is valid (default: 7)

        Returns:
            InviteToken instance
        """
        return cls(
            token=token,
            project_id=project_id,
            email=email,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=days_valid),
        )

    def is_valid(self) -> bool:
        """
        Check if token is still valid.

        Returns:
            True if token is not expired and not used
        """
        return (
            self.used_at is None
            and datetime.now(timezone.utc) < self.expires_at
        )

    def mark_as_used(self):
        """Mark the token as used."""
        self.used_at = datetime.now(timezone.utc)
