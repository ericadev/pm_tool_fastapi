from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid
from app.models import User
from app.database import get_db
from app.schemas.user import UserResponse, UserCreateRequest
from app.schemas.auth import LoginRequest, TokenResponse
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token

router = APIRouter()

def _user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse, converting datetime to ISO strings."""
    return UserResponse(
        id=user.id,
        email=user.email,
        firstName=user.firstName,
        lastName=user.lastName,
        avatar=user.avatar,
        createdAt=user.createdAt.isoformat() if isinstance(user.createdAt, datetime) else user.createdAt,
        updatedAt=user.updatedAt.isoformat() if isinstance(user.updatedAt, datetime) else user.updatedAt,
    )


@router.get("/")
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [_user_to_response(user) for user in users]

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreateRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User with this email already exists."
        )

    hashed_password = hash_password(user.password)
    now = datetime.now(timezone.utc)
    db_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        password=hashed_password,
        firstName=user.firstName,
        lastName=user.lastName,
        createdAt=now,
        updatedAt=now,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return _user_to_response(db_user)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)
    return TokenResponse(access_token=access_token, token_type="bearer")