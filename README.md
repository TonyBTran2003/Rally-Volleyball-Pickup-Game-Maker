# Rally-Volleyball-Pickup-Game-Maker

Rally is a full-stack pickup volleyball platform designed to help players create, discover, join, and manage local volleyball games.

The project started as a functional full-stack MVP and has been expanded into a more production-ready backend system with automated testing, database migrations, validation, query optimization, and structured logging.

---

## What Rally Is Today

Rally currently supports the core workflow of a pickup sports platform.

Users can:

- Register and log in
- Create volleyball games
- Browse available games
- Filter and paginate games
- Join and leave games
- View player counts
- Edit games they created
- Delete their own games
- Log out securely

### Current Tech Stack

#### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

#### Frontend

- HTML
- CSS
- Vanilla JavaScript

#### Authentication

- JWT authentication
- Argon2 password hashing
- Protected API routes
- Ownership-based authorization

#### Database

- PostgreSQL
- SQLAlchemy ORM
- Alembic migrations
- Foreign keys
- Unique constraints
- Database indexes
- Many-to-many game membership

#### Testing

- pytest
- FastAPI TestClient
- HTTPX
- Separate PostgreSQL test database

---

## Current Backend Architecture

Rally separates HTTP routing from business logic.

```text
Frontend
   |
   | HTTP / JSON
   v
FastAPI Routers
   |
   v
Service Layer
   |
   v
SQLAlchemy
   |
   v
PostgreSQL
```

The backend is organized into areas such as:

```text
backend/app/
├── routers/
│   ├── auth.py
│   ├── games.py
│   └── users.py
│
├── services/
│   ├── auth_service.py
│   └── game_service.py
│
├── models/
├── schemas/
├── core/
├── database.py
└── main.py
```

Routers handle HTTP requests and responses, while the service layer contains application and database logic.

---

## Authentication

Rally uses JWT-based authentication.

```text
Register
   ↓
Password hashed with Argon2
   ↓
User stored in PostgreSQL

Login
   ↓
Credentials verified
   ↓
JWT returned
   ↓
Bearer token sent with protected requests
```

Protected actions include:

- Creating games
- Updating games
- Deleting games
- Joining games
- Leaving games

Only the creator of a game can update or delete it.

---

## Game Management

Users can create volleyball games with information such as:

- Title
- Description
- Location
- Date
- Start time
- Maximum players
- Skill level
- Game format

The creator is automatically added as the first player.

Rally supports full CRUD functionality through both the REST API and frontend:

```text
Create → Create a game
Read   → Browse and view games
Update → Edit a game
Delete → Delete a game
```

Rally also tracks player membership using a separate `game_players` table.

```text
users
   |
   | creator_id
   v
games
   |
   | game_id
   v
game_players
   ^
   | user_id
   |
users
```

A unique constraint prevents the same user from joining the same game more than once.

---

## Concurrency Protection

Rally includes protection against race conditions when multiple users try to join the final available spot in a game.

The backend locks the game row while checking player capacity:

```python
select(Game).where(
    Game.id == game_id
).with_for_update()
```

This helps prevent a game from exceeding its maximum number of players during concurrent join requests.

---

## Validation and Error Handling

Rally includes both request validation and application-level business validation.

Examples include:

- Game dates cannot be in the past
- Titles and locations cannot contain only whitespace
- Game capacity cannot be reduced below the current player count
- Duplicate joins are rejected
- Users cannot join full games
- Game creators cannot leave their own games
- Non-creators cannot edit or delete games
- Invalid authentication tokens are rejected

The API uses appropriate HTTP status codes such as `400`, `401`, `403`, `404`, `409`, and `422` depending on the type of failure.

---

## Pagination and Filtering

The game discovery endpoint supports pagination and filtering.

Examples:

```text
GET /games?page=1&page_size=20

GET /games?skill_level=intermediate

GET /games?format=6v6

GET /games?status=open

GET /games?skill_level=advanced&format=6v6&page=2
```

Pagination limits the number of games returned per request, while filtering is performed directly in PostgreSQL.

---

## Database Optimization

Rally includes database indexes designed around common game queries, including filtering by status, skill level, and game date.

The game listing endpoint was also optimized to remove an N+1 query pattern.

Previously, returning 20 games could require approximately:

```text
1 query to retrieve games
20 additional queries to count players
```

Player counts are now calculated using a grouped SQL subquery and joined to the game results, reducing the number of database queries required when listing games.

---

## Database Migrations

Rally uses Alembic to manage database schema changes.

Instead of automatically creating tables when the application starts, database changes are versioned through migration files.

Example workflow:

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

This makes the database schema reproducible across development, testing, and future deployment environments.

---

## Automated Testing

Rally includes API integration tests using pytest and FastAPI TestClient.

Tests run against a dedicated PostgreSQL database:

```text
Development:
rally_db

Testing:
rally_test
```

This prevents automated tests from modifying development data.

Current tests cover functionality such as:

- User registration
- Duplicate account handling
- Login
- Incorrect passwords
- Protected endpoints
- Game creation
- Game validation
- Pagination and filtering
- Joining games
- Duplicate joins
- Leaving games
- Full-game protection
- Player count updates
- Creator restrictions
- Update and delete authorization
- Missing game handling

Tests can be run with:

```bash
pytest -v
```

---

## Logging

Rally includes structured application logging for HTTP requests and important business events.

Request logs include:

```text
method
path
status code
response time
```

Application events include:

```text
user_registered
game_created
game_joined
game_left
game_deleted
```

Warnings are also logged for events such as failed authentication, duplicate joins, and attempts to join full games.

Sensitive information such as passwords and JWTs is not logged.

---

## Development Seed Data

Rally includes a seed script for quickly creating realistic development users, games, and memberships.

Run:

```bash
python -m scripts.seed_demo
```

The seed script is separate from automated test data and is intended for development and manual testing.

---

# What Rally Will Become

The long-term goal is to evolve Rally from a production-oriented full-stack application into a scalable distributed system.

The next phases will focus on distributed infrastructure, real-time features, performance testing, and deployment.

---

## Phase 2 — Production Quality

Phase 2 focused on improving the quality, maintainability, and performance of the original MVP.

Completed improvements include:

- Alembic database migrations
- Automated API testing
- Separate PostgreSQL test database
- Service-layer architecture
- Stronger request and business validation
- Improved error handling
- Pagination
- Game filtering
- Database indexes
- N+1 query optimization
- Structured logging
- Expanded authorization and edge-case tests
- Development seed data
- Full frontend CRUD functionality

---

## Phase 3 — Scalability

Rally will next be expanded to support a more distributed architecture.

Planned technologies include:

- Docker
- Redis
- Nginx
- Background workers
- Multiple FastAPI instances
- WebSockets

A future architecture may look like:

```text
Browser
   |
   v
Nginx
   |
   +-------------------+
   |         |         |
   v         v         v
FastAPI   FastAPI   FastAPI
   |         |         |
   +---------+---------+
             |
       +-----+-----+
       |           |
       v           v
     Redis     PostgreSQL
       |
       v
Background Workers
```

Redis may be used for caching, shared application state, and reducing repeated database work.

Docker will allow the application and its dependencies to run consistently across development and deployment environments.

Nginx will act as a reverse proxy and load balancer in front of multiple FastAPI instances.

---

## Real-Time Features

Rally may eventually support real-time updates using WebSockets.

Examples include:

- Live player counts
- Game updates
- Join and leave notifications
- Game status changes
- Waitlist notifications

Instead of refreshing the page, users could receive updates immediately when another player interacts with a game.

---

## Background Processing

Some operations do not need to happen during the user's HTTP request.

Future background jobs may handle:

- Notifications
- Email delivery
- Game reminders
- Waitlist promotion
- Cleanup tasks
- Analytics processing

Moving these tasks to workers will help keep API requests fast.

---

## Waitlist System

A future Rally game may support:

```text
12 / 12 players
Game Full

Waitlist:
1. Player A
2. Player B
3. Player C
```

If a player leaves:

```text
Player leaves
     ↓
open position detected
     ↓
first waitlisted player promoted
     ↓
notification sent
```

This will introduce additional concurrency and distributed-system challenges.

---

## Phase 4 — Performance and Deployment

The final phase will focus on proving how Rally behaves under load.

Planned tools and techniques include:

- Locust load testing
- Throughput measurements
- Concurrent-user testing
- p50 latency
- p95 latency
- p99 latency
- Error-rate tracking
- Performance profiling
- CI/CD
- Cloud deployment

Rather than simply claiming Rally is scalable, the goal is to measure it.

Future performance documentation will use actual measured results such as:

```text
Concurrent users: <measured value>
Requests/second: <measured value>
p95 latency: <measured value>
p99 latency: <measured value>
Error rate: <measured value>
```

---

## Project Goal

Rally is intended to demonstrate the full evolution of a backend system:

```text
Working MVP
    ↓
Clean architecture
    ↓
Automated testing
    ↓
Database migrations
    ↓
Validation
    ↓
Pagination and filtering
    ↓
Database optimization
    ↓
Logging and observability
    ↓
Containerization
    ↓
Caching
    ↓
Background processing
    ↓
Horizontal scaling
    ↓
Load testing
    ↓
Deployment
```

The goal is not only to build a volleyball application, but to use Rally as a practical environment for learning and demonstrating full-stack development, backend engineering, database design, concurrency, testing, performance optimization, and scalable system design.
