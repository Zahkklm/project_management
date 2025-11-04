from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.invite_token import InviteToken
from app.models.project import Project
from app.models.user import User


class InvitationResponse(BaseModel):
    token: str
    project_id: int
    project_name: str
    expires_at: datetime

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("/invitations", response_model=List[InvitationResponse])
def get_pending_invitations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all pending invitations for current user."""
    invites = (
        db.query(InviteToken, Project.name)
        .join(Project, InviteToken.project_id == Project.id)
        .filter(
            InviteToken.email == current_user.email,
            InviteToken.used_at.is_(None),
            InviteToken.expires_at > datetime.utcnow(),
        )
        .all()
    )

    return [
        {
            "token": invite.InviteToken.token,
            "project_id": invite.InviteToken.project_id,
            "project_name": invite.name,
            "expires_at": invite.InviteToken.expires_at,
        }
        for invite in invites
    ]
