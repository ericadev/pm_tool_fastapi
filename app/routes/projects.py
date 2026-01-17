from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4
from app.models import Project, User
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectResponse
from app.dependencies.auth import get_current_user

router = APIRouter()


@router.get("/")
def read_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [ProjectResponse.model_validate(project) for project in projects]


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new project. Requires authentication."""
    now = datetime.utcnow()
    new_project = Project(
        id=str(uuid4()),
        name=project.name,
        description=project.description,
        color=project.color,
        icon=project.icon,
        ownerId=current_user.id,
        createdAt=now,
        updatedAt=now,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return ProjectResponse.model_validate(new_project)
