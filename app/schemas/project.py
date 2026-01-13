from pydantic import BaseModel


class ProjectResponse(BaseModel):
    id: str
    name: str
    ownerId: str
    createdAt: str
    updatedAt: str
    description: str | None
    color: str | None
    icon: str | None

    class Config:
        from_attributes = True
