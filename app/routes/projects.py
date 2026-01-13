from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Project
from app.database import get_db
from app.schemas.project import ProjectResponse

router = APIRouter()


@router.get("/")
def read_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [ProjectResponse.from_orm(project) for project in projects]
