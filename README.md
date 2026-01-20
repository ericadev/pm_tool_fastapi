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

### Development with Docker

You can also run the application with Docker for a consistent development environment:

```bash
docker-compose up --build
```

This will:
1. Start a PostgreSQL database container
2. Run all database migrations automatically
3. Start the FastAPI server on port 8000

The database will be available at `localhost:5432` and the API at `http://localhost:8000`.

## Deployment

### Option 1: Railway (Recommended)

Railway is the easiest option for deploying this FastAPI application with PostgreSQL.

**Setup:**
1. Sign up at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Create a new project and select "Deploy from GitHub"
4. Select this repository
5. Railway will automatically detect FastAPI and create a Dockerfile
6. Add PostgreSQL service:
   - Click "Add Service" → "PostgreSQL"
   - Railway will configure database credentials automatically
7. Set environment variables in Railway dashboard:
   ```
   JWT_SECRET_KEY=<generate-strong-secret>
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_DAYS=7
   CORS_ORIGINS=https://your-frontend-domain.com
   ```
8. Deploy!

Railway will automatically:
- Build the Docker image
- Run database migrations
- Start the application
- Provide a public URL

**Cost:** Railway offers a free tier with generous limits.

### Option 2: Docker + Self-Hosted VPS

Deploy on any VPS (DigitalOcean, AWS, Linode, etc.):

**Build and Push to Registry:**
```bash
# Build image
docker build -t pm-tool-backend:latest .

# Tag for registry (example: Docker Hub)
docker tag pm-tool-backend:latest yourusername/pm-tool-backend:latest

# Push to registry
docker push yourusername/pm-tool-backend:latest
```

**On VPS:**
```bash
# Pull image
docker pull yourusername/pm-tool-backend:latest

# Create docker-compose.yml with production settings
docker-compose -f docker-compose.production.yml up -d
```

### Option 3: Traditional Python Deployment

For a traditional VPS without Docker:

```bash
# On server
git clone https://github.com/ericadev/pm_tool_fastapi.git
cd pm_tool_fastapi
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start with production server (Gunicorn)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

Use a reverse proxy (Nginx) for SSL/TLS termination and load balancing.

### Environment Variables for Production

Ensure these are set on your deployment platform:

```env
DATABASE_USER=pm_tool_user
DATABASE_PASSWORD=<strong-password>
DATABASE_HOST=<database-host>
DATABASE_PORT=5432
DATABASE_NAME=pm_tool

JWT_SECRET_KEY=<generate-with: python -c "import secrets; print(secrets.token_urlsafe(32))">
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

### Health Checks

The application includes a root endpoint for health checks:

```bash
curl https://your-api-domain.com/
# Response: {"message": "Hello World"}
```

This can be used by load balancers and monitoring services.

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
