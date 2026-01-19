from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict


class TaskStatus(str, Enum):
    """Task status enumeration."""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    DONE = "DONE"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str
    description: str | None = None
    projectId: str
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assigneeId: str | None = None
    dueDate: datetime | None = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigneeId: str | None = None
    dueDate: datetime | None = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None
    projectId: str
    creatorId: str
    assigneeId: str | None
    status: TaskStatus
    priority: TaskPriority
    position: int
    dueDate: datetime | None
    createdAt: datetime
    updatedAt: datetime
