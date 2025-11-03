import secrets
from typing import List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_project_role
from app.core.config import settings
from app.core.database import get_db
from app.models.invite_token import InviteToken
from app.models.project import Project
from app.models.project_access import ProjectAccess
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

PROJECT_NOT_FOUND = "Project not found"

router = APIRouter()

# RBAC is now handled by require_project_role in deps.py


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    project_access = ProjectAccess(
        project_id=new_project.id, user_id=current_user.id, role="owner"
    )
    db.add(project_access)
    db.commit()

    return new_project


@router.get("/projects", response_model=List[ProjectListResponse])
def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accesses = (
        db.query(ProjectAccess)
        .filter(ProjectAccess.user_id == current_user.id)
        .all()
    )
    project_ids = [access.project_id for access in accesses]
    projects = db.query(Project).filter(Project.id.in_(project_ids)).all()
    return projects


@router.get("/project/{project_id}/info", response_model=ProjectResponse)
def get_project_info(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_project_role(project_id, db, current_user)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PROJECT_NOT_FOUND
        )
    return project


@router.put("/project/{project_id}/info", response_model=ProjectResponse)
def update_project_info(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_project_role(project_id, db, current_user)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PROJECT_NOT_FOUND
        )
    if project_data.name is not None:
        setattr(project, "name", project_data.name)
    if project_data.description is not None:
        setattr(project, "description", project_data.description)
    db.commit()
    db.refresh(project)
    return project


@router.delete(
    "/project/{project_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_project_role(project_id, db, current_user, role="owner")
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PROJECT_NOT_FOUND
        )
    db.delete(project)
    db.commit()


@router.post("/project/{project_id}/invite", status_code=status.HTTP_200_OK)
def invite_user_to_project(
    project_id: int,
    user: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_project_role(project_id, db, current_user, role="owner")
    invited_user = db.query(User).filter(User.login == user).first()
    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    existing_access = (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == invited_user.id,
        )
        .first()
    )
    if existing_access:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("User already has access to this project"),
        )
    project_access = ProjectAccess(
        project_id=project_id, user_id=invited_user.id, role="participant"
    )
    db.add(project_access)
    db.commit()
    return {"message": "User invited successfully"}


@router.get("/project/{project_id}/share", status_code=status.HTTP_200_OK)
def share_project_via_email(
    project_id: int,
    with_email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Share a project via email invitation."""
    from app.services.mock_email_service import MockEmailService
    from app.services.ses_email_service import SESEmailService

    # Verify user is project owner
    require_project_role(project_id, db, current_user, role="owner")

    # Get project details
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PROJECT_NOT_FOUND
        )

    # Generate secure token
    token = secrets.token_urlsafe(32)

    # Create invite token record in database
    invite_token = InviteToken.create_token(
        token=token, project_id=project_id, email=with_email, days_valid=7
    )
    db.add(invite_token)
    db.commit()

    # Generate join link
    join_link = (
        f"{settings.FRONTEND_URL}/join?token={token}&project_id={project_id}"
    )

    # Send email (use mock in dev, SES in production)
    if settings.USE_MOCK_EMAIL:
        email_service = MockEmailService()  # type: ignore[assignment]
    else:
        email_service = SESEmailService(  # type: ignore[assignment]
            sender_email=settings.SES_SENDER_EMAIL,
            aws_region=settings.SES_AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    background_tasks.add_task(
        email_service.send_invite_email,
        recipient_email=with_email,
        project_name=project.name,
        inviter_name=current_user.email,
        join_link=join_link,
    )

    return {
        "message": f"Invite link sent to {with_email}",
        "join_link": join_link,
    }


@router.post("/join", status_code=status.HTTP_200_OK)
def join_project_via_token(
    token: str,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Join a project using an invitation token."""
    # Find the invite token
    invite_token = (
        db.query(InviteToken)
        .filter(
            InviteToken.token == token, InviteToken.project_id == project_id
        )
        .first()
    )

    if not invite_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invitation token",
        )

    # Verify token is still valid
    if not invite_token.is_valid():
        if invite_token.used_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invitation has already been used",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invitation has expired",
            )

    # Verify token was sent to current user's email
    if invite_token.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation was sent to a different email address",
        )

    # Check if user already has access
    existing_access = (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == current_user.id,
        )
        .first()
    )

    if existing_access:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have access to this project",
        )

    # Grant access
    project_access = ProjectAccess(
        project_id=project_id, user_id=current_user.id, role="participant"
    )
    db.add(project_access)

    # Mark token as used
    invite_token.mark_as_used()

    db.commit()

    return {
        "message": "Successfully joined project",
        "project_id": project_id,
    }
