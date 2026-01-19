import pytest
from fastapi import status
from datetime import datetime, timedelta


class TestTaskCreation:
    """Tests for task creation endpoint."""

    def test_create_task_success(self, client, test_user):
        """Test successful task creation."""
        # First create a project
        project_data = {
            "name": "Test Project",
            "description": "A test project"
        }
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        assert project_response.status_code == status.HTTP_201_CREATED
        project_id = project_response.json()["id"]

        # Create a task
        task_data = {
            "title": "Test Task",
            "description": "A test task",
            "projectId": project_id,
            "status": "TODO",
            "priority": "MEDIUM"
        }
        response = client.post(
            "/tasks/",
            json=task_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["projectId"] == project_id
        assert data["status"] == "TODO"
        assert data["priority"] == "MEDIUM"
        assert data["creatorId"] == test_user["user"]["id"]
        assert "id" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_create_task_without_token(self, client):
        """Test task creation without token returns 401 or 403."""
        task_data = {
            "title": "Test Task",
            "projectId": "some-project-id"
        }
        response = client.post("/tasks/", json=task_data)

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_create_task_with_invalid_project(self, client, test_user):
        """Test task creation with invalid project returns 404."""
        task_data = {
            "title": "Test Task",
            "projectId": "nonexistent-project-id"
        }
        response = client.post(
            "/tasks/",
            json=task_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Project not found" in response.json()["detail"]

    def test_create_task_with_invalid_assignee(self, client, test_user):
        """Test task creation with invalid assignee returns 404."""
        # Create a project first
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        # Try to create task with invalid assignee
        task_data = {
            "title": "Test Task",
            "projectId": project_id,
            "assigneeId": "nonexistent-user-id"
        }
        response = client.post(
            "/tasks/",
            json=task_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Assignee not found" in response.json()["detail"]

    def test_create_task_with_assignee(self, client):
        """Test creating task with valid assignee."""
        # Create two users
        user1_data = {
            "email": "user1@tasks.com",
            "password": "password123"
        }
        user1_response = client.post("/users/", json=user1_data)
        user1_id = user1_response.json()["id"]

        user2_data = {
            "email": "user2@tasks.com",
            "password": "password123"
        }
        user2_response = client.post("/users/", json=user2_data)
        user2_id = user2_response.json()["id"]

        # Login as user1
        login1 = client.post("/users/login", json=user1_data)
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # User1 creates project
        project_data = {"name": "Task Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=headers1
        )
        project_id = project_response.json()["id"]

        # Create task and assign to user2
        task_data = {
            "title": "Task for User 2",
            "projectId": project_id,
            "assigneeId": user2_id
        }
        response = client.post(
            "/tasks/",
            json=task_data,
            headers=headers1
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["assigneeId"] == user2_id

    def test_create_task_with_due_date(self, client, test_user):
        """Test creating task with due date."""
        # Create a project
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        # Create task with due date
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Task with Due Date",
            "projectId": project_id,
            "dueDate": due_date
        }
        response = client.post(
            "/tasks/",
            json=task_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["dueDate"] is not None


class TestTaskRetrieval:
    """Tests for task retrieval endpoints."""

    def test_get_task_success(self, client, test_user):
        """Test getting a specific task."""
        # Create project and task
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        task_data = {
            "title": "Test Task",
            "projectId": project_id
        }
        task_response = client.post(
            "/tasks/",
            json=task_data,
            headers=test_user["headers"]
        )
        task_id = task_response.json()["id"]

        # Get the task
        response = client.get(f"/tasks/{task_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"

    def test_get_nonexistent_task(self, client):
        """Test getting nonexistent task returns 404."""
        response = client.get("/tasks/nonexistent-task-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Task not found" in response.json()["detail"]

    def test_list_tasks(self, client, test_user):
        """Test listing all tasks."""
        # Create project
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        # Create multiple tasks
        for i in range(3):
            task_data = {
                "title": f"Task {i+1}",
                "projectId": project_id
            }
            client.post(
                "/tasks/",
                json=task_data,
                headers=test_user["headers"]
            )

        # List tasks
        response = client.get("/tasks/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3

    def test_list_tasks_filter_by_project(self, client, test_user):
        """Test listing tasks filtered by project."""
        # Create two projects
        project1_data = {"name": "Project 1"}
        project1_response = client.post(
            "/projects/",
            json=project1_data,
            headers=test_user["headers"]
        )
        project1_id = project1_response.json()["id"]

        project2_data = {"name": "Project 2"}
        project2_response = client.post(
            "/projects/",
            json=project2_data,
            headers=test_user["headers"]
        )
        project2_id = project2_response.json()["id"]

        # Create tasks in both projects
        for i in range(2):
            client.post(
                "/tasks/",
                json={"title": f"Task {i+1}", "projectId": project1_id},
                headers=test_user["headers"]
            )

        client.post(
            "/tasks/",
            json={"title": "Task 3", "projectId": project2_id},
            headers=test_user["headers"]
        )

        # List tasks for project1
        response = client.get(f"/tasks/?project_id={project1_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(task["projectId"] == project1_id for task in data)

    def test_list_tasks_filter_by_status(self, client, test_user):
        """Test listing tasks filtered by status."""
        # Create project
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        # Create tasks with different statuses
        client.post(
            "/tasks/",
            json={"title": "TODO Task", "projectId": project_id, "status": "TODO"},
            headers=test_user["headers"]
        )

        client.post(
            "/tasks/",
            json={"title": "Done Task", "projectId": project_id, "status": "DONE"},
            headers=test_user["headers"]
        )

        # List TODO tasks
        response = client.get("/tasks/?status=TODO")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(task["status"] == "TODO" for task in data)


class TestTaskUpdate:
    """Tests for task update endpoint."""

    def test_update_task_success(self, client, test_user):
        """Test successful task update."""
        # Create project and task
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        task_data = {
            "title": "Original Title",
            "projectId": project_id,
            "status": "TODO",
            "priority": "LOW"
        }
        task_response = client.post(
            "/tasks/",
            json=task_data,
            headers=test_user["headers"]
        )
        task_id = task_response.json()["id"]

        # Update task
        update_data = {
            "title": "Updated Title",
            "status": "IN_PROGRESS",
            "priority": "HIGH"
        }
        response = client.patch(
            f"/tasks/{task_id}",
            json=update_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "IN_PROGRESS"
        assert data["priority"] == "HIGH"

    def test_update_nonexistent_task(self, client, test_user):
        """Test updating nonexistent task returns 404."""
        update_data = {"title": "Updated Title"}
        response = client.patch(
            "/tasks/nonexistent-task-id",
            json=update_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task_partial(self, client, test_user):
        """Test partial task update (only some fields)."""
        # Create project and task
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        task_data = {
            "title": "Original Title",
            "description": "Original Description",
            "projectId": project_id
        }
        task_response = client.post(
            "/tasks/",
            json=task_data,
            headers=test_user["headers"]
        )
        task_id = task_response.json()["id"]

        # Update only title
        update_data = {"title": "New Title"}
        response = client.patch(
            f"/tasks/{task_id}",
            json=update_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "Original Description"

    def test_update_task_without_token(self, client, test_user):
        """Test task update without token returns 401 or 403."""
        # Create a task first
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        task_data = {"title": "Test Task", "projectId": project_id}
        task_response = client.post(
            "/tasks/",
            json=task_data,
            headers=test_user["headers"]
        )
        task_id = task_response.json()["id"]

        # Try to update without token
        update_data = {"title": "Updated"}
        response = client.patch(f"/tasks/{task_id}", json=update_data)

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_update_task_with_invalid_assignee(self, client, test_user):
        """Test updating task with invalid assignee returns 404."""
        # Create project and task
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        task_data = {"title": "Test Task", "projectId": project_id}
        task_response = client.post(
            "/tasks/",
            json=task_data,
            headers=test_user["headers"]
        )
        task_id = task_response.json()["id"]

        # Try to update with invalid assignee
        update_data = {"assigneeId": "nonexistent-user-id"}
        response = client.patch(
            f"/tasks/{task_id}",
            json=update_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTaskDeletion:
    """Tests for task deletion endpoint."""

    def test_delete_task_success(self, client, test_user):
        """Test successful task deletion."""
        # Create project and task
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        task_data = {"title": "Test Task", "projectId": project_id}
        task_response = client.post(
            "/tasks/",
            json=task_data,
            headers=test_user["headers"]
        )
        task_id = task_response.json()["id"]

        # Delete task
        response = client.delete(
            f"/tasks/{task_id}",
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify task is deleted
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_task(self, client, test_user):
        """Test deleting nonexistent task returns 404."""
        response = client.delete(
            "/tasks/nonexistent-task-id",
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_without_token(self, client, test_user):
        """Test task deletion without token returns 401 or 403."""
        # Create a task first
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        task_data = {"title": "Test Task", "projectId": project_id}
        task_response = client.post(
            "/tasks/",
            json=task_data,
            headers=test_user["headers"]
        )
        task_id = task_response.json()["id"]

        # Try to delete without token
        response = client.delete(f"/tasks/{task_id}")

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestTaskStatuses:
    """Tests for task status management."""

    def test_task_status_enum_values(self, client, test_user):
        """Test all valid task statuses."""
        # Create project
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        statuses = ["TODO", "IN_PROGRESS", "IN_REVIEW", "DONE"]

        for status_val in statuses:
            task_data = {
                "title": f"Task with {status_val}",
                "projectId": project_id,
                "status": status_val
            }
            response = client.post(
                "/tasks/",
                json=task_data,
                headers=test_user["headers"]
            )

            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["status"] == status_val

    def test_task_priority_enum_values(self, client, test_user):
        """Test all valid task priorities."""
        # Create project
        project_data = {"name": "Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = project_response.json()["id"]

        priorities = ["LOW", "MEDIUM", "HIGH", "URGENT"]

        for priority_val in priorities:
            task_data = {
                "title": f"Task with {priority_val}",
                "projectId": project_id,
                "priority": priority_val
            }
            response = client.post(
                "/tasks/",
                json=task_data,
                headers=test_user["headers"]
            )

            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["priority"] == priority_val
