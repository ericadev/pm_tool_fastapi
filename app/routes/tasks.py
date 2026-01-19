from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

from app.models import Task, Project, User
from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.dependencies.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    project_id: str | None = None,
    status: str | None = None,
    assignee_id: str | None = None,
    db: Session = Depends(get_db),
):
    """Get all tasks, optionally filtered by project, status, or assignee."""
    query = db.query(Task)

    if project_id:
        query = query.filter(Task.projectId == project_id)

    if status:
        query = query.filter(Task.status == status)

    if assignee_id:
        query = query.filter(Task.assigneeId == assignee_id)

    tasks = query.all()
    return [TaskResponse.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get a specific task by ID."""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse.model_validate(task)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task. Requires authentication."""
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == task_data.projectId).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Verify assignee exists if provided
    if task_data.assigneeId:
        assignee = db.query(User).filter(User.id == task_data.assigneeId).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found"
            )

    now = datetime.utcnow()
    new_task = Task(
        id=str(uuid4()),
        title=task_data.title,
        description=task_data.description,
        projectId=task_data.projectId,
        creatorId=current_user.id,
        assigneeId=task_data.assigneeId,
        status=task_data.status,
        priority=task_data.priority,
        dueDate=task_data.dueDate,
        position=0,
        createdAt=now,
        updatedAt=now,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return TaskResponse.model_validate(new_task)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a task. Requires authentication."""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify assignee exists if provided
    if task_data.assigneeId:
        assignee = db.query(User).filter(User.id == task_data.assigneeId).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found"
            )

    # Update fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.status is not None:
        task.status = task_data.status
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.assigneeId is not None:
        task.assigneeId = task_data.assigneeId
    if task_data.dueDate is not None:
        task.dueDate = task_data.dueDate

    task.updatedAt = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a task. Requires authentication."""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return None
