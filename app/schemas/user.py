from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    email: str
    firstName: str | None
    lastName: str | None
    avatar: str | None
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True
