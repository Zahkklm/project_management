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
from app.core.database import get_db
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
    from app.services.mock_email_service import MockEmailService

    require_project_role(project_id, db, current_user, role="owner")
    token = secrets.token_urlsafe(32)
    join_link = (
        f"https://yourdomain.com/join?token={token}&project_id={project_id}"
    )
    email_service = MockEmailService()
    background_tasks.add_task(
        email_service.send_invite_email, with_email, join_link
    )
    return {
        "message": f"Invite link sent to {with_email}",
        "join_link": join_link,
    }
