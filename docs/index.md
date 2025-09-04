# FastAPI Backend Documentation

## Table of Contents

- [Project Overview](#project-overview)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Users](#users)
  - [Profiles](#profiles)
  - [Notifications](#notifications)
- [Development Guide](#development-guide)
  - [Setup](#setup)
  - [Project Structure](#project-structure)
  - [Testing](#testing)
  - [Code Quality](#code-quality)
- [Deployment](#deployment)
  - [Docker](#docker)
  - [CI/CD](#cicd)

## Project Overview

This is a FastAPI backend service with a repository/service architecture pattern. The system implements user authentication, profile management, notification system, private messaging system, and role-based access control (RBAC) using modern Python tools and best practices.

The notification system allows users to receive and manage notifications with different types (info, success, warning, error) and statuses (read, unread). Users can send notifications to other users, retrieve their notifications, mark them as read, and delete them.

The messaging system allows users to send private messages to other users, manage their inbox and sent messages, and perform CRUD operations on their messages.

## API Endpoints

### Authentication

#### Register a new user
```
POST /api/v1/auth/register
```
Registers a new user and creates an empty profile.

#### Login
```
POST /api/v1/auth/login
```
Authenticates a user and returns JWT tokens.

#### Refresh token
```
POST /api/v1/auth/refresh
```
Refreshes the access token using a refresh token.

#### Logout
```
POST /api/v1/auth/logout
```
Revokes the current refresh token.

#### Logout from all devices
```
POST /api/v1/auth/logout-all
```
Revokes all refresh tokens for the user.

#### Request password reset
```
POST /api/v1/auth/request-password-reset
```
Requests a password reset email.

#### Confirm password reset
```
POST /api/v1/auth/confirm-password-reset
```
Confirms password reset with a token.

### Users

#### Get current user
```
GET /api/v1/users/me
```
Gets the current user (without profile). Requires authentication.

#### Get specific user
```
GET /api/v1/users/{id}
```
Gets a specific user. Requires admin role.

#### Update specific user
```
PATCH /api/v1/users/{id}
```
Updates a specific user. Requires admin role.

#### List all users
```
GET /api/v1/users
```
Lists all users. Requires admin role.

### Profiles

#### Get current user's profile
```
GET /api/v1/profiles/me
```
Gets the current user's profile. Requires authentication.

#### Update current user's profile
```
PATCH /api/v1/profiles/me
```
Updates the current user's profile. Requires authentication.

#### Get specific user's profile
```
GET /api/v1/profiles/{user_id}
```
Gets a specific user's profile. Requires admin role.

#### Update specific user's profile
```
PATCH /api/v1/profiles/{user_id}
```
Updates a specific user's profile. Requires admin role.

### Notifications

#### Send a notification
```
POST /api/v1/notifications/
```
Send a notification to a user. Requires authentication.

Request body:
```json
{
  "title": "string",
  "message": "string",
  "type": "info|success|warning|error",
  "user_id": "uuid"
}
```

#### Get user notifications
```
GET /api/v1/notifications/
```
Get notifications for the current user. Supports filtering by status. Requires authentication.

Query parameters:
- `status`: Filter by notification status (unread|read)
- `limit`: Number of notifications to return (default: 100)
- `offset`: Offset for pagination (default: 0)

Response:
```json
{
  "notifications": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "string",
      "message": "string",
      "type": "info|success|warning|error",
      "status": "unread|read",
      "is_read": "boolean",
      "read_at": "datetime|null",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": "integer"
}
```

#### Get unread notification count
```
GET /api/v1/notifications/unread-count
```
Get the count of unread notifications for the current user. Requires authentication.

Response:
```json
{
  "count": "integer"
}
```

#### Get a specific notification
```
GET /api/v1/notifications/{notification_id}
```
Get a specific notification. Requires authentication and ownership of the notification.

Response:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "message": "string",
  "type": "info|success|warning|error",
  "status": "unread|read",
  "is_read": "boolean",
  "read_at": "datetime|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Update a notification
```
PATCH /api/v1/notifications/{notification_id}
```
Update a notification. Requires authentication and ownership of the notification.

Request body:
```json
{
  "title": "string|null",
  "message": "string|null",
  "type": "info|success|warning|error|null",
  "status": "unread|read|null",
  "is_read": "boolean|null"
}
```

#### Mark notifications as read
```
POST /api/v1/notifications/mark-as-read
```
Mark multiple notifications as read. Requires authentication and ownership of all notifications.

Request body:
```json
{
  "notification_ids": ["uuid"]
}
```

#### Delete a notification
```
DELETE /api/v1/notifications/{notification_id}
```
Delete a notification. Requires authentication and ownership of the notification.

### Messages

#### Send a message
```
POST /api/v1/messages/
```
Send a message to a user. Requires authentication.

Request body:
```json
{
  "recipient_id": "uuid",
  "subject": "string",
  "content": "string"
}
```

#### Get inbox
```
GET /api/v1/messages/inbox
```
Get messages received by the current user. Requires authentication.

Query parameters:
- `skip`: Number of messages to skip (default: 0)
- `limit`: Maximum number of messages to return (default: 100)

Response:
```json
{
  "messages": [
    {
      "id": "uuid",
      "sender_id": "uuid",
      "recipient_id": "uuid",
      "subject": "string",
      "content": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": "integer"
}
```

#### Get sent messages
```
GET /api/v1/messages/sent
```
Get messages sent by the current user. Requires authentication.

Query parameters:
- `skip`: Number of messages to skip (default: 0)
- `limit`: Maximum number of messages to return (default: 100)

Response:
```json
{
  "messages": [
    {
      "id": "uuid",
      "sender_id": "uuid",
      "recipient_id": "uuid",
      "subject": "string",
      "content": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": "integer"
}
```

#### Get a specific message
```
GET /api/v1/messages/{message_id}
```
Get a specific message. Requires authentication and ownership (sender or recipient) of the message.

Response:
```json
{
  "id": "uuid",
  "sender_id": "uuid",
  "recipient_id": "uuid",
  "subject": "string",
  "content": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Update a message
```
PATCH /api/v1/messages/{message_id}
```
Update a message. Requires authentication and ownership (sender only) of the message.

Request body:
```json
{
  "subject": "string|null",
  "content": "string|null"
}
```

#### Delete a message
```
DELETE /api/v1/messages/{message_id}
```
Delete a message. Requires authentication and ownership (sender or recipient) of the message.

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
  domain/               # Domain modules (users, profiles, auth, notifications)
    users/              # User management
    profiles/           # Profile management
    auth/               # Authentication
    notifications/      # Notification system
    messages/           # Private messaging system
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