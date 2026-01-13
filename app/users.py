from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import User
from app.database import get_db

router = APIRouter()

@router.get("/")
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users