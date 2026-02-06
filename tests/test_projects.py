import pytest
from fastapi import status


class TestProjectCreation:
    """Tests for project creation endpoint."""

    def test_create_project_success(self, client, test_user):
        """Test successful project creation."""
        project_data = {
            "name": "Test Project",
            "description": "A test project",
            "color": "#FF5733",
            "icon": "📋"
        }
        response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert data["color"] == project_data["color"]
        assert data["icon"] == project_data["icon"]
        assert data["ownerId"] == test_user["user"]["id"]
        assert "id" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_create_project_minimal_data(self, client, test_user):
        """Test project creation with only required fields."""
        project_data = {
            "name": "Simple Project"
        }
        response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Simple Project"
        assert data["description"] is None
        assert data["color"] == "#3b82f6"  # Default color from database
        assert data["icon"] == "folder"  # Default icon from database
        assert data["ownerId"] == test_user["user"]["id"]

    def test_create_project_without_token(self, client):
        """Test project creation without authentication returns 401 or 403."""
        project_data = {
            "name": "Unauthorized Project"
        }
        response = client.post("/projects/", json=project_data)

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_create_project_missing_name(self, client, test_user):
        """Test project creation without name returns 422."""
        project_data = {
            "description": "No name provided"
        }
        response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_multiple_projects_same_user(self, client, test_user):
        """Test creating multiple projects for the same user."""
        project_names = ["Project 1", "Project 2", "Project 3"]
        project_ids = []

        for name in project_names:
            response = client.post(
                "/projects/",
                json={"name": name},
                headers=test_user["headers"]
            )
            assert response.status_code == status.HTTP_201_CREATED
            project_ids.append(response.json()["id"])

        # Verify all projects are unique
        assert len(project_ids) == len(set(project_ids))

    def test_create_projects_different_users(self, client):
        """Test that different users can create projects."""
        # Create first user
        user1_data = {
            "email": "user1@projects.com",
            "password": "password123",
            "firstName": "User",
            "lastName": "One"
        }
        user1_response = client.post("/users/", json=user1_data)
        assert user1_response.status_code == status.HTTP_200_OK
        user1_id = user1_response.json()["id"]

        # Create second user
        user2_data = {
            "email": "user2@projects.com",
            "password": "password123",
            "firstName": "User",
            "lastName": "Two"
        }
        user2_response = client.post("/users/", json=user2_data)
        assert user2_response.status_code == status.HTTP_200_OK
        user2_id = user2_response.json()["id"]

        # Login as user1
        login1 = client.post("/users/login", json={
            "email": user1_data["email"],
            "password": user1_data["password"]
        })
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Login as user2
        login2 = client.post("/users/login", json={
            "email": user2_data["email"],
            "password": user2_data["password"]
        })
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User1 creates a project
        project1_response = client.post(
            "/projects/",
            json={"name": "User 1 Project"},
            headers=headers1
        )
        assert project1_response.status_code == status.HTTP_201_CREATED
        assert project1_response.json()["ownerId"] == user1_id

        # User2 creates a project
        project2_response = client.post(
            "/projects/",
            json={"name": "User 2 Project"},
            headers=headers2
        )
        assert project2_response.status_code == status.HTTP_201_CREATED
        assert project2_response.json()["ownerId"] == user2_id


class TestProjectRetrieval:
    """Tests for project retrieval endpoints."""

    def test_read_projects_success(self, client, test_user):
        """Test reading projects returns only user's projects."""
        # Create some projects
        project_names = ["Project A", "Project B", "Project C"]
        for name in project_names:
            client.post(
                "/projects/",
                json={"name": name},
                headers=test_user["headers"]
            )

        # Read projects
        response = client.get(
            "/projects/",
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert all(p["ownerId"] == test_user["user"]["id"] for p in data)
        assert all(p["name"] in project_names for p in data)

    def test_read_projects_user_isolation(self, client):
        """Test that users only see their own projects."""
        # Create two users
        user1_data = {
            "email": "isolation_user1@test.com",
            "password": "password123"
        }
        user1_response = client.post("/users/", json=user1_data)
        user1_id = user1_response.json()["id"]

        user2_data = {
            "email": "isolation_user2@test.com",
            "password": "password123"
        }
        user2_response = client.post("/users/", json=user2_data)
        user2_id = user2_response.json()["id"]

        # Login as user1
        login1 = client.post("/users/login", json={
            "email": user1_data["email"],
            "password": user1_data["password"]
        })
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Login as user2
        login2 = client.post("/users/login", json={
            "email": user2_data["email"],
            "password": user2_data["password"]
        })
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User1 creates 2 projects
        project1_resp = client.post(
            "/projects/",
            json={"name": "User1 Project 1"},
            headers=headers1
        )
        project1_id = project1_resp.json()["id"]

        client.post(
            "/projects/",
            json={"name": "User1 Project 2"},
            headers=headers1
        )

        # User2 creates 1 project
        project2_resp = client.post(
            "/projects/",
            json={"name": "User2 Project 1"},
            headers=headers2
        )
        project2_id = project2_resp.json()["id"]

        # User1 reads projects - should see only their 2 projects
        user1_projects = client.get(
            "/projects/",
            headers=headers1
        ).json()
        assert len(user1_projects) == 2
        assert all(p["ownerId"] == user1_id for p in user1_projects)

        # User2 reads projects - should see only their 1 project
        user2_projects = client.get(
            "/projects/",
            headers=headers2
        ).json()
        assert len(user2_projects) == 1
        assert user2_projects[0]["ownerId"] == user2_id
        assert user2_projects[0]["id"] == project2_id

        # User2 cannot see User1's projects
        assert all(p["id"] != project1_id for p in user2_projects)

    def test_read_projects_without_token(self, client):
        """Test reading projects without authentication returns 401 or 403."""
        response = client.get("/projects/")

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_read_projects_empty(self, client, test_user):
        """Test reading projects when user has no projects."""
        response = client.get(
            "/projects/",
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0

    def test_read_projects_returns_all_fields(self, client, test_user):
        """Test that read projects response includes all fields."""
        # Create a project with all fields
        project_data = {
            "name": "Full Project",
            "description": "Full description",
            "color": "#123456",
            "icon": "🎯"
        }
        create_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        created_project = create_response.json()

        # Read projects
        read_response = client.get(
            "/projects/",
            headers=test_user["headers"]
        )
        projects = read_response.json()

        assert len(projects) == 1
        project = projects[0]

        # Verify all fields are present
        assert project["id"] == created_project["id"]
        assert project["name"] == project_data["name"]
        assert project["description"] == project_data["description"]
        assert project["color"] == project_data["color"]
        assert project["icon"] == project_data["icon"]
        assert project["ownerId"] == test_user["user"]["id"]
        assert "createdAt" in project
        assert "updatedAt" in project

    def test_read_projects_response_format(self, client, test_user):
        """Test that read projects response has correct data types."""
        client.post(
            "/projects/",
            json={"name": "Test Project"},
            headers=test_user["headers"]
        )

        response = client.get(
            "/projects/",
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_200_OK
        projects = response.json()
        assert isinstance(projects, list)
        assert len(projects) > 0

        project = projects[0]
        assert isinstance(project["id"], str)
        assert isinstance(project["name"], str)
        assert isinstance(project["ownerId"], str)
        assert isinstance(project["createdAt"], str)
        assert isinstance(project["updatedAt"], str)
        assert project["description"] is None or isinstance(project["description"], str)
        assert isinstance(project["color"], str)  # Has database default
        assert isinstance(project["icon"], str)  # Has database default


class TestProjectDetail:
    """Tests for getting a specific project by ID."""

    def test_get_project_success(self, client, test_user):
        """Test getting a specific project by ID."""
        # Create a project
        project_data = {
            "name": "Detail Project",
            "description": "A project for testing details",
            "color": "#FF0000",
            "icon": "📊"
        }
        create_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project_id = create_response.json()["id"]

        # Get the project
        response = client.get(
            f"/projects/{project_id}",
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert data["color"] == project_data["color"]
        assert data["icon"] == project_data["icon"]
        assert data["ownerId"] == test_user["user"]["id"]

    def test_get_project_without_token(self, client):
        """Test getting project without authentication returns 401 or 403."""
        response = client.get("/projects/nonexistent-project-id")

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_get_nonexistent_project(self, client, test_user):
        """Test getting nonexistent project returns 404."""
        response = client.get(
            "/projects/nonexistent-project-id",
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Project not found" in response.json()["detail"]

    def test_get_other_users_project(self, client):
        """Test that users cannot see other users' projects."""
        # Create first user and project
        user1_data = {
            "email": "user1_detail@test.com",
            "password": "password123"
        }
        user1_response = client.post("/users/", json=user1_data)
        user1_id = user1_response.json()["id"]

        # Login as user1
        login1 = client.post("/users/login", json={
            "email": user1_data["email"],
            "password": user1_data["password"]
        })
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # User1 creates a project
        project_response = client.post(
            "/projects/",
            json={"name": "User 1 Secret Project"},
            headers=headers1
        )
        project_id = project_response.json()["id"]

        # Create second user
        user2_data = {
            "email": "user2_detail@test.com",
            "password": "password123"
        }
        user2_response = client.post("/users/", json=user2_data)

        # Login as user2
        login2 = client.post("/users/login", json={
            "email": user2_data["email"],
            "password": user2_data["password"]
        })
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User2 tries to get User1's project - should get 404
        response = client.get(
            f"/projects/{project_id}",
            headers=headers2
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Project not found" in response.json()["detail"]

    def test_get_project_returns_all_fields(self, client, test_user):
        """Test that get project response includes all fields."""
        # Create a project with all fields
        project_data = {
            "name": "Complete Project",
            "description": "Complete description",
            "color": "#123ABC",
            "icon": "🎨"
        }
        create_response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )
        project_id = create_response.json()["id"]

        # Get the project
        response = client.get(
            f"/projects/{project_id}",
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_200_OK
        project = response.json()

        # Verify all fields are present
        assert "id" in project
        assert "name" in project
        assert "description" in project
        assert "color" in project
        assert "icon" in project
        assert "ownerId" in project
        assert "createdAt" in project
        assert "updatedAt" in project
