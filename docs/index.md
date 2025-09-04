# FastAPI Backend Documentation

## Table of Contents

- [Project Overview](#project-overview)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Users](#users)
  - [Profiles](#profiles)
- [Development Guide](#development-guide)
  - [Setup](#setup)
  - [Project Structure](#project-structure)
  - [Testing](#testing)
  - [Code Quality](#code-quality)
- [Deployment](#deployment)
  - [Docker](#docker)
  - [CI/CD](#cicd)

## Project Overview

This is a FastAPI backend service with a repository/service architecture pattern. The system implements user authentication, profile management, and role-based access control (RBAC) using modern Python tools and best practices.

## API Endpoints

### Authentication

#### Register a new user
```
POST /auth/register
```
Registers a new user and creates an empty profile.

#### Login
```
POST /auth/login
```
Authenticates a user and returns JWT tokens.

#### Refresh token
```
POST /auth/refresh
```
Refreshes the access token using a refresh token.

#### Logout
```
POST /auth/logout
```
Revokes the current refresh token.

#### Logout from all devices
```
POST /auth/logout-all
```
Revokes all refresh tokens for the user.

#### Request password reset
```
POST /auth/request-password-reset
```
Requests a password reset email.

#### Confirm password reset
```
POST /auth/confirm-password-reset
```
Confirms password reset with a token.

### Users

#### Get current user
```
GET /users/me
```
Gets the current user (without profile). Requires authentication.

#### Get specific user
```
GET /users/{id}
```
Gets a specific user. Requires admin role.

#### Update specific user
```
PATCH /users/{id}
```
Updates a specific user. Requires admin role.

#### List all users
```
GET /users
```
Lists all users. Requires admin role.

### Profiles

#### Get current user's profile
```
GET /profiles/me
```
Gets the current user's profile. Requires authentication.

#### Update current user's profile
```
PATCH /profiles/me
```
Updates the current user's profile. Requires authentication.

#### Get specific user's profile
```
GET /profiles/{user_id}
```
Gets a specific user's profile. Requires admin role.

#### Update specific user's profile
```
PATCH /profiles/{user_id}
```
Updates a specific user's profile. Requires admin role.

## Development Guide

### Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   make install-dev
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

### Project Structure

The project follows a domain-driven design with the following structure:

```
app/
  core/                 # Core utilities and configuration
  db/                   # Database configuration
  di/                   # Dependency injection
  api/                  # API routers and dependencies
  domain/               # Domain modules (users, profiles, auth)
    users/              # User management
    profiles/           # Profile management
    auth/               # Authentication
  utils/                # Utility functions
```

### Testing

Run tests with:
```bash
make test
```

Run tests with coverage:
```bash
make test-cov
```

### Code Quality

The project uses several tools to ensure code quality:

- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **MyPy**: Static type checking

Run all quality checks:
```bash
make check-quality
```

Format code:
```bash
make format
```

## Deployment

### Docker

To run with Docker:
```bash
docker-compose up --build
```

### CI/CD

The project includes GitHub Actions workflows:

- **CI Pipeline**: Runs on every push and pull request
- **Deployment Pipeline**: Runs when a new release is published