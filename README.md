# User Management Service

A RESTful user management service built with **FastAPI**, developed as part of a Python Backend internship in 2024.

The project covers user authentication, authorization, profile management, and integration with external services using an asynchronous backend architecture.

## Tech Stack

- **Backend:** Python 3.10, FastAPI, Pydantic
- **Database:** PostgreSQL, SQLAlchemy (async), Alembic
- **Authentication:** JWT, bcrypt, Redis
- **Messaging:** RabbitMQ
- **Storage:** Amazon S3 (LocalStack, aioboto3)
- **Infrastructure:** Docker, Docker Compose
- **Testing:** Pytest, HTTPX, pytest-asyncio
- **CI/CD:** GitHub Actions, pre-commit

## Features

- User registration and authentication
- JWT access and refresh tokens
- Password hashing with bcrypt
- Role-based access control (Admin, Moderator, User)
- User profile management and CRUD operations
- Pagination, filtering, and sorting
- Profile image uploads to S3-compatible storage
- Password reset workflow using RabbitMQ
- Database migrations with Alembic
- Unit and integration tests

## Architecture

The application separates API endpoints, business logic, database operations, and external integrations.

### Main Components

- `auth/` — Authentication, JWT management, and password reset
- `users/` — User management and access control
- `models/` — SQLAlchemy database models
- `core/` — Configuration, database connections, and utilities
- `integrations/` — RabbitMQ and S3 integrations
- `alembic/` — Database migrations
- `tests/` — Unit and integration tests

### Service Communication

The service uses RabbitMQ to publish password reset messages, which can be processed by a separate Notification Service.

Redis is used for refresh token storage, PostgreSQL stores user data, and LocalStack emulates AWS S3 for local development.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Run the Application

```bash
git clone https://github.com/sashcheka/user-management-service.git
cd user-management-service

docker compose up -d --build
```

The application is configured to run on port `5000`.

API documentation:

http://localhost:5000/docs

Health check:

http://localhost:5000/healthcheck/

The `dev.env` file contains local development configuration. Credentials and JWT signing keys should be replaced with local development values and never reused in production.

## Testing

The project contains unit and integration tests using Pytest.

Run the test environment:

```bash
docker compose -f docker-compose-test.yml up -d --build

docker compose -f docker-compose-test.yml run --rm web-test pytest tests/ --cov=src

docker compose -f docker-compose-test.yml down
```

GitHub Actions is configured to run checks and tests on pushes and pull requests.

## Related Project

[Notification Service](https://github.com/sashcheka/notification-service) — processes password reset messages using RabbitMQ, MongoDB, and AWS SES.

## Project Status

Educational internship project (2024).

The code demonstrates backend development and service integration patterns. It is not production-hardened and requires additional security and reliability improvements before real-world deployment.
