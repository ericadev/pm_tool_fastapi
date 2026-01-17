from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    firstName: str | None
    lastName: str | None
    avatar: str | None
    createdAt: datetime
    updatedAt: datetime

class UserCreateRequest(BaseModel):
    email: str
    password: str
    firstName: str | None = None
    lastName: str | None = None