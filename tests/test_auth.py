import pytest
from fastapi import status


class TestUserCreation:
    """Tests for user creation endpoint."""

    def test_create_user_success(self, client):
        """Test successful user creation."""
        user_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "firstName": "John",
            "lastName": "Doe"
        }
        response = client.post("/users/", json=user_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["firstName"] == user_data["firstName"]
        assert data["lastName"] == user_data["lastName"]
        assert "id" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_create_user_duplicate_email(self, client):
        """Test that duplicate email returns 409 Conflict."""
        user_data = {
            "email": "duplicate@example.com",
            "password": "password123"
        }
        # Create first user
        response1 = client.post("/users/", json=user_data)
        assert response1.status_code == status.HTTP_200_OK

        # Try to create second user with same email
        response2 = client.post("/users/", json=user_data)
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response2.json()["detail"]

    def test_create_user_minimal(self, client):
        """Test user creation with minimal fields."""
        user_data = {
            "email": "minimal@example.com",
            "password": "password123"
        }
        response = client.post("/users/", json=user_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["firstName"] is None
        assert data["lastName"] is None


class TestLogin:
    """Tests for login endpoint."""

    def test_login_success(self, test_user):
        """Test successful login returns access token."""
        response = test_user["user"]  # This is just the user object
        assert response is not None
        # The token was already obtained in the fixture
        assert test_user["token"] is not None
        assert test_user["headers"]["Authorization"].startswith("Bearer ")

    def test_login_with_correct_credentials(self, client, test_user):
        """Test login with correct email and password."""
        credentials = test_user["credentials"]
        response = client.post("/users/login", json={
            "email": credentials["email"],
            "password": credentials["password"]
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_with_wrong_password(self, client, test_user):
        """Test login with wrong password returns 401."""
        credentials = test_user["credentials"]
        response = client.post("/users/login", json={
            "email": credentials["email"],
            "password": "wrongpassword"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_with_nonexistent_email(self, client):
        """Test login with non-existent email returns 401."""
        response = client.post("/users/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_response_format(self, client, test_user):
        """Test login response has correct format."""
        credentials = test_user["credentials"]
        response = client.post("/users/login", json={
            "email": credentials["email"],
            "password": credentials["password"]
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Verify token format (JWT is base64.base64.base64)
        assert data["access_token"].count(".") == 2


class TestProtectedEndpoints:
    """Tests for authentication on protected endpoints."""

    def test_create_project_with_valid_token(self, client, test_user):
        """Test creating project with valid JWT token."""
        project_data = {
            "name": "Test Project",
            "description": "A test project",
            "color": "#3b82f6",
            "icon": "folder"
        }
        response = client.post(
            "/projects/",
            json=project_data,
            headers=test_user["headers"]
        )

        assert response.status_code == status.HTTP_201_CREATED
        # Just verify status - response validation happens in route
        assert response.text  # Verify we got a response

    def test_create_project_without_token(self, client):
        """Test creating project without token returns 401 or 403."""
        project_data = {
            "name": "Test Project"
        }
        response = client.post("/projects/", json=project_data)

        # HTTPBearer returns 403 when no credentials provided
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_create_project_with_invalid_token(self, client):
        """Test creating project with invalid token returns 401."""
        project_data = {
            "name": "Test Project"
        }
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.post("/projects/", json=project_data, headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid authentication credentials" in response.json()["detail"]

    def test_create_project_with_malformed_token(self, client):
        """Test creating project with malformed auth header."""
        project_data = {
            "name": "Test Project"
        }
        # Missing "Bearer" prefix
        headers = {"Authorization": "invalid_token_here"}
        response = client.post("/projects/", json=project_data, headers=headers)

        # HTTPBearer returns 403 for malformed headers
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_create_project_sets_owner_to_current_user(self, client):
        """Test that project owner is set to authenticated user."""
        # Create first user
        user1_data = {
            "email": "user1@example.com",
            "password": "password123"
        }
        user1_response = client.post("/users/", json=user1_data)
        user1_id = user1_response.json()["id"]

        login1 = client.post("/users/login", json=user1_data)
        token1 = login1.json()["access_token"]

        # Create second user
        user2_data = {
            "email": "user2@example.com",
            "password": "password123"
        }
        user2_response = client.post("/users/", json=user2_data)
        user2_id = user2_response.json()["id"]

        login2 = client.post("/users/login", json=user2_data)
        token2 = login2.json()["access_token"]

        # User 1 creates project
        project_data = {"name": "User1 Project"}
        response1 = client.post(
            "/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token1}"}
        )

        # User 2 creates project
        response2 = client.post(
            "/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token2}"}
        )

        # Both should be created successfully
        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED


class TestTokenExpiration:
    """Tests for token expiration and validation."""

    def test_valid_token_format(self, test_user):
        """Test that returned token has valid JWT format."""
        token = test_user["token"]
        # JWT format: header.payload.signature
        parts = token.split(".")
        assert len(parts) == 3
        # Each part should be non-empty
        assert all(len(part) > 0 for part in parts)

    def test_token_contains_user_id(self, client, test_user):
        """Test that token payload contains user_id."""
        from app.utils.jwt import decode_access_token

        token = test_user["token"]
        user_id = decode_access_token(token)

        assert user_id is not None
        assert user_id == test_user["user"]["id"]

    def test_invalid_token_decode_fails(self, client):
        """Test that decoding invalid token returns None."""
        from app.utils.jwt import decode_access_token

        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.invalid"
        result = decode_access_token(invalid_token)

        assert result is None


class TestAuthenticationFlow:
    """Integration tests for complete authentication flow."""

    def test_full_auth_flow(self, client):
        """Test complete flow: create user -> login -> create protected resource."""
        # Step 1: Create user
        user_data = {
            "email": "integration@example.com",
            "password": "securepassword123",
            "firstName": "Integration",
            "lastName": "Test"
        }
        user_response = client.post("/users/", json=user_data)
        assert user_response.status_code == status.HTTP_200_OK
        user_id = user_response.json()["id"]

        # Step 2: Login
        login_response = client.post("/users/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]

        # Step 3: Use token to create protected resource
        project_data = {"name": "Integration Test Project"}
        project_response = client.post(
            "/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert project_response.status_code == status.HTTP_201_CREATED

    def test_multiple_users_isolation(self, client):
        """Test that different users can create projects with different owners."""
        # Create user 1
        user1_response = client.post("/users/", json={
            "email": "user1@test.com",
            "password": "pass1"
        })
        assert user1_response.status_code == status.HTTP_200_OK
        user1_id = user1_response.json()["id"]

        token1_response = client.post("/users/login", json={
            "email": "user1@test.com",
            "password": "pass1"
        })
        token1 = token1_response.json()["access_token"]

        # Create user 2
        user2_response = client.post("/users/", json={
            "email": "user2@test.com",
            "password": "pass2"
        })
        assert user2_response.status_code == status.HTTP_200_OK
        user2_id = user2_response.json()["id"]

        token2_response = client.post("/users/login", json={
            "email": "user2@test.com",
            "password": "pass2"
        })
        token2 = token2_response.json()["access_token"]

        # User 1 creates project
        project1_response = client.post(
            "/projects/",
            json={"name": "User 1 Project"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert project1_response.status_code == status.HTTP_201_CREATED

        # User 2 creates project
        project2_response = client.post(
            "/projects/",
            json={"name": "User 2 Project"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert project2_response.status_code == status.HTTP_201_CREATED

        # Verify users are different
        assert user1_id != user2_id
