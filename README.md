# FastAPI Backend Project

This is a FastAPI backend service with a repository/service architecture pattern. The system implements user authentication, profile management, notification system, and role-based access control (RBAC) using modern Python tools and best practices.

## Features

- User authentication with JWT tokens
- Profile management system
- Notification system with real-time capabilities
- Private messaging system between users
- Role-based access control (client, executor, admin)
- Password reset functionality with email verification
- Database migrations with Alembic
- Dependency injection with Dishka

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **ASGI Server**: Uvicorn
- **Database**: SQLite with SQLAlchemy 2.0 (AsyncSession)
- **Migrations**: Alembic
- **Dependency Injection**: Dishka
- **Data Validation**: Pydantic v2
- **Security**: Passlib (bcrypt/argon2), PyJWT
- **Email**: aiosmtplib
- **Configuration**: python-dotenv
- **Testing**: pytest, httpx, pytest-asyncio
- **Code Quality**: ruff, black, mypy

## Project Structure

```
app/
  core/
    config.py          # Application configuration
    security.py        # Password hashing and verification
    jwt.py             # JWT token creation and validation
    email.py           # Email sending functionality
  db/
    base.py            # Base database models
    session.py         # Database session management
  domain/
    users/
      models.py        # User database model
      schemas.py       # User Pydantic schemas
      repository.py    # User data access layer
      service.py       # User business logic
      router.py        # User API endpoints
      enums.py         # User-related enums
      policies.py      # User access policies
    profiles/
      models.py        # Profile database model
      schemas.py       # Profile Pydantic schemas
      repository.py    # Profile data access layer
      service.py       # Profile business logic
      router.py        # Profile API endpoints
    auth/
      router.py        # Authentication API endpoints
      schemas.py       # Auth Pydantic schemas
      service.py       # Authentication business logic
      repository.py    # Auth data access layer
    notifications/
      models.py        # Notification database model
      schemas.py       # Notification Pydantic schemas
      repository.py    # Notification data access layer
      service.py       # Notification business logic
      router.py        # Notification API endpoints
      enums.py         # Notification-related enums
    messages/
      models.py        # Message database model
      schemas.py       # Message Pydantic schemas
      repository.py    # Message data access layer
      service.py       # Message business logic
      router.py        # Message API endpoints
  di/
    container.py       # Dependency injection container
  api/
    deps.py            # API dependencies
    router.py          # Main API router
  utils/
    crypto.py          # Cryptographic utilities
    exceptions.py      # Custom exceptions
  main.py              # Application entry point
alembic/
  env.py               # Alembic configuration
  versions/            # Database migration scripts
docs/                  # Documentation
scripts/               # Development scripts
tests/
  test_auth.py         # Authentication tests
  test_users.py        # User functionality tests
  test_profiles.py     # Profile functionality tests
  test_notifications.py # Notification functionality tests
.env.example           # Environment variables example
README.md              # Project documentation
```

## Setup

### Quick Setup

Run the initialization script:
```bash
./scripts/init-dev.sh
```

### Manual Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   make install-dev
   ```
   
   Or using pip directly:
   ```bash
   pip install -r requirements.txt
   ```
   
   For development, install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
   
   Or install in development mode with all dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the server:
   ```bash
   make dev
   ```
   
   Or directly:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user and create empty profile
- `POST /api/v1/auth/login` - Authenticate user and return JWT tokens
- `POST /api/v1/auth/refresh` - Refresh access token using refresh token
- `POST /api/v1/auth/logout` - Revoke current refresh token
- `POST /api/v1/auth/logout-all` - Revoke all refresh tokens for user
- `POST /api/v1/auth/request-password-reset` - Request password reset email
- `POST /api/v1/auth/confirm-password-reset` - Confirm password reset with token

### Users
- `GET /api/v1/users/me` - Get current user (without profile) - Authenticated
- `GET /api/v1/users/{id}` - Get specific user - Admin
- `PATCH /api/v1/users/{id}` - Update specific user - Admin
- `GET /api/v1/users` - List all users - Admin

### Profiles
- `GET /api/v1/profiles/me` - Get current user's profile - Authenticated
- `PATCH /api/v1/profiles/me` - Update current user's profile - Authenticated
- `GET /api/v1/profiles/{user_id}` - Get specific user's profile - Admin
- `PATCH /api/v1/profiles/{user_id}` - Update specific user's profile - Admin

### Notifications
- `POST /api/v1/notifications/` - Send a notification to a user - Authenticated
- `GET /api/v1/notifications/` - Get notifications for the current user - Authenticated
- `GET /api/v1/notifications/unread-count` - Get count of unread notifications - Authenticated
- `GET /api/v1/notifications/{notification_id}` - Get a specific notification - Authenticated
- `PATCH /api/v1/notifications/{notification_id}` - Update a notification - Authenticated
- `POST /api/v1/notifications/mark-as-read` - Mark multiple notifications as read - Authenticated
- `DELETE /api/v1/notifications/{notification_id}` - Delete a notification - Authenticated

### Messages
- `POST /api/v1/messages/` - Send a message to a user - Authenticated
- `GET /api/v1/messages/inbox` - Get messages received by the current user - Authenticated
- `GET /api/v1/messages/sent` - Get messages sent by the current user - Authenticated
- `GET /api/v1/messages/{message_id}` - Get a specific message - Authenticated
- `PATCH /api/v1/messages/{message_id}` - Update a message (sender only) - Authenticated
- `DELETE /api/v1/messages/{message_id}` - Delete a message (sender or recipient) - Authenticated

## Testing

Run tests with:
```bash
make test
```

Or with coverage:
```bash
make test-cov
```

Or using the script:
```bash
./scripts/test-coverage.sh
```

## Code Quality

The project uses several tools to ensure code quality:

- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **MyPy**: Static type checking

Run all code quality checks:
```bash
make check-quality
```

Or using the script:
```bash
./scripts/code-quality.sh
```

Format code:
```bash
make format
```

## CI/CD Pipeline

This project includes GitHub Actions workflows for continuous integration and deployment:

- **CI Pipeline** ([.github/workflows/ci.yml](file:///Users/a1111/Desktop/works/api/.github/workflows/ci.yml)): Runs on every push and pull request to the main branch
  - Tests execution across Python 3.11 and 3.12
  - Code formatting check with black
  - Code linting with ruff
  - Type checking with mypy
  - Build validation

- **Deployment Pipeline** ([.github/workflows/deploy.yml](file:///Users/a1111/Desktop/works/api/.github/workflows/deploy.yml)): Runs when a new release is published
  - Database migrations
  - Application deployment
  - Health checks

## Docker Support

The project includes Docker configuration for containerized deployment:

- **[Dockerfile](file:///Users/a1111/Desktop/works/api/Dockerfile)**: Multi-stage build for production deployment
- **[docker-compose.yml](file:///Users/a1111/Desktop/works/api/docker-compose.yml)**: For local development with PostgreSQL

To run with Docker:
```bash
# Build and run the application
docker-compose up --build

# Run tests in Docker
docker-compose run api pytest
```

To build and run the Docker image directly:
```bash
# Build the image
docker build -t fastapi-backend .

# Run the container
docker run -p 8000:8000 fastapi-backend
```

The Docker setup includes all features of the application, including the messaging system, notification system, and user management.

## Project Configuration

The project uses modern Python packaging standards:

- **[pyproject.toml](file:///Users/a1111/Desktop/works/api/pyproject.toml)**: Main project configuration (PEP 621)
- **[setup.py](file:///Users/a1111/Desktop/works/api/setup.py)**: Backward compatibility
- **[setup.cfg](file:///Users/a1111/Desktop/works/api/setup.cfg)**: Additional configuration for flake8, pytest, and mypy
- **[requirements.txt](file:///Users/a1111/Desktop/works/api/requirements.txt)**: Production dependencies
- **[requirements-dev.txt](file:///Users/a1111/Desktop/works/api/requirements-dev.txt)**: Development dependencies

## Development Scripts

The project includes helpful scripts in the `scripts/` directory:

- **[init-dev.sh](file:///Users/a1111/Desktop/works/api/scripts/init-dev.sh)**: Initialize the development environment
- **[code-quality.sh](file:///Users/a1111/Desktop/works/api/scripts/code-quality.sh)**: Run all code quality checks
- **[test-coverage.sh](file:///Users/a1111/Desktop/works/api/scripts/test-coverage.sh)**: Run tests with coverage reports

## Documentation

Documentation is available in the `docs/` directory:

- **[index.md](file:///Users/a1111/Desktop/works/api/docs/index.md)**: Main documentation file

## Makefile Commands

The project includes a Makefile with common commands:

- `make install` - Install production dependencies
- `make install-dev` - Install development dependencies
- `make test` - Run tests
- `make test-cov` - Run tests with coverage
- `make lint` - Run code linting
- `make format` - Format code with black
- `make check-quality` - Run all quality checks
- `make run` - Run the application
- `make dev` - Run the application in development mode
- `make clean` - Clean up generated files