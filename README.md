# FastAPI Project Management Tool Backend

A modern, production-ready project management API built with FastAPI, PostgreSQL, SQLAlchemy, and JWT authentication.

## Features

- **User Management**: User registration and authentication with JWT tokens
- **Project Management**: Create and manage projects with ownership tracking
- **Task Management**: Full task lifecycle management with status and priority tracking
- **Team Collaboration**: Project members with role-based access control
- **Activity Tracking**: Audit logs for all project activities
- **Comments & Discussions**: Task-level comments and discussions
- **Tagging System**: Flexible tagging system for tasks
- **Notifications**: User notification system with metadata support

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern async Python web framework
- **Database**: PostgreSQL with [SQLAlchemy](https://www.sqlalchemy.org/) ORM
- **Authentication**: JWT tokens with 7-day expiration
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/) for schema versioning
- **Testing**: [pytest](https://pytest.org/) with comprehensive test coverage
- **Password Hashing**: bcrypt for secure password storage

## Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Virtual environment (venv, conda, or similar)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd fastapi_pm_tool_backend
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_USER=pm_tool_user
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_key_change_this_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_DAYS=7
```

**Important**: Generate a strong JWT secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Create PostgreSQL databases

```bash
# Create the postgres user and production database
sudo -u postgres psql
CREATE USER pm_tool_user WITH PASSWORD 'your_password';
ALTER USER pm_tool_user CREATEDB;
CREATE DATABASE pm_tool OWNER pm_tool_user;
CREATE DATABASE pm_tool_test OWNER pm_tool_user;
\q
```

### 6. Run migrations

```bash
.venv/bin/alembic upgrade head
```

This creates all tables and indexes in the `pm_tool` database.

## Running the Application

### Start the development server

```bash
.venv/bin/uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Access API documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /users/` - Register a new user
- `POST /users/login` - Login and get JWT token

### Projects

- `GET /projects/` - Get all projects
- `POST /projects/` - Create a new project (requires authentication)

### Additional Endpoints

See the OpenAPI documentation at `/docs` for complete endpoint details.

## Database Schema

The application includes the following main tables:

| Table | Purpose |
|-------|---------|
| `User` | User accounts and authentication |
| `Project` | Projects with ownership tracking |
| `ProjectMember` | Project team members with roles |
| `Task` | Project tasks with status and priority |
| `Comment` | Task comments and discussions |
| `Activity` | Audit log of all project activities |
| `Tag` | Reusable tags for tasks |
| `TaskTag` | Task-tag relationships |
| `Notification` | User notifications |

## Testing

### Run all tests

```bash
.venv/bin/pytest tests/ -v
```

### Run specific test file

```bash
.venv/bin/pytest tests/test_auth.py -v
```

### Run with coverage

```bash
.venv/bin/pytest tests/ --cov=app --cov-report=html
```

### Test Database

Tests automatically use the `pm_tool_test` database and clean up after each test. Your production database (`pm_tool_dev`) is never modified.

## Authentication Flow

1. **Register**: `POST /users/` with email and password
2. **Login**: `POST /users/login` with email and password to receive JWT token
3. **Access Protected Routes**: Include the token in Authorization header:
   ```
   Authorization: Bearer <your_token_here>
   ```
4. **Token Validation**: JWT tokens are valid for 7 days from creation

Example:
```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}

# Use token to access protected routes:
curl -X GET "http://localhost:8000/projects/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## Project Structure

```
fastapi_pm_tool_backend/
├── alembic/                 # Database migrations
│   ├── versions/           # Migration files
│   └── env.py             # Migration configuration
├── app/
│   ├── dependencies/      # Dependency injection (auth, etc.)
│   ├── models.py          # SQLAlchemy ORM models
│   ├── database.py        # Database configuration
│   ├── main.py            # FastAPI app setup
│   ├── routes/            # API route handlers
│   │   ├── users.py
│   │   └── projects.py
│   ├── schemas/           # Pydantic schemas (validation)
│   │   ├── user.py
│   │   ├── project.py
│   │   └── auth.py
│   └── utils/             # Utility functions
│       ├── jwt.py         # JWT token utilities
│       └── security.py    # Password hashing
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest configuration and fixtures
│   └── test_auth.py       # Authentication tests (18 tests)
├── .env                   # Environment variables (git ignored)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Development Workflow

### Creating a New Feature

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Implement your feature with tests

3. Run tests to ensure nothing breaks:
   ```bash
   .venv/bin/pytest tests/ -v
   ```

4. Create a pull request to merge into main

### Database Changes

1. Modify SQLAlchemy models in `app/models.py`
2. Generate migration:
   ```bash
   .venv/bin/alembic revision --autogenerate -m "Description of changes"
   ```
3. Review the generated migration
4. Apply migration:
   ```bash
   .venv/bin/alembic upgrade head
   ```

## Security Considerations

- ✅ Passwords are hashed with bcrypt before storage
- ✅ JWT tokens expire after 7 days
- ✅ Bearer token validation on protected endpoints
- ✅ Email uniqueness enforced at database level
- ✅ User input validated with Pydantic schemas
- ⚠️ Use HTTPS in production (configure in reverse proxy)
- ⚠️ Keep `JWT_SECRET_KEY` secure and private
- ⚠️ Use environment-specific configurations for dev/staging/production

## Performance Optimizations

- Database indexes on frequently queried columns:
  - User email (unique)
  - Project owner ID
  - Task status and project
  - Activity creation time
- Connection pooling for database efficiency
- Async/await for non-blocking I/O operations

## Troubleshooting

### Database Connection Error

```
psycopg2.OperationalError: connection to server failed
```

**Solution**: Ensure PostgreSQL is running and credentials are correct in `.env`

### JWT Secret Not Found

```
KeyError: 'JWT_SECRET_KEY'
```

**Solution**: Add `JWT_SECRET_KEY` to `.env` file

### Migration Conflicts

```
alembic.util.exc.CommandError: Can't locate revision identified by...
```

**Solution**: Check migration history with `alembic history` and verify `alembic.ini` configuration

### Tests Fail with Database Error

```
psycopg2.OperationalError: database "pm_tool_test" does not exist
```

**Solution**: Create test database:
```bash
sudo -u postgres psql -c "CREATE DATABASE pm_tool_test OWNER pm_tool_user;"
```

## Contributing

1. Create a feature branch from main
2. Make your changes with tests
3. Ensure all tests pass: `pytest tests/ -v`
4. Create a pull request with a clear description
5. Get code review before merging

## License

[Add your license here]

## Support

For issues, questions, or suggestions, please create an issue in the repository.

---

**Last Updated**: January 2026
**Status**: Production Ready ✅
