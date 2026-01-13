from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Project
from app.database import get_db

router = APIRouter()

@router.get("/")
def read_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects