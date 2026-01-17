from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    color: str | None = None
    icon: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    ownerId: str
    createdAt: datetime
    updatedAt: datetime
    description: str | None
    color: str | None
    icon: str | None
