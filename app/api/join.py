from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.project_access import ProjectAccess
from app.models.user import User

router = APIRouter()


@router.get("/join", status_code=status.HTTP_200_OK)
def join_project(token: str, project_id: int, db: Session = Depends(get_db)):
    # Simulate token validation: token is user login for demo
    user = db.query(User).filter(User.login == token).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="Invalid token or user not found"
        )
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    existing_access = (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user.id,
        )
        .first()
    )
    if existing_access:
        return {"message": "User already has access to this project"}
    project_access = ProjectAccess(
        project_id=project_id, user_id=user.id, role="participant"
    )
    db.add(project_access)
    db.commit()
    return {
        "message": f"User {user.login} joined project {project_id} successfully"
    }
