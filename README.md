# Rally-Volleyball-Pickup-Game-Maker

Rally is a full-stack pickup volleyball platform designed to help players create, discover, join, and manage local volleyball games.

The project started as a functional full-stack MVP and is being expanded into a more production-ready and scalable backend system.

---

## What Rally Is Today

Rally currently supports the core workflow of a pickup sports platform.

Users can:

- Register and log in
- Create volleyball games
- Browse available games
- Join and leave games
- View player counts
- Manage games they created
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

Rally includes basic protection against race conditions when multiple users try to join the final available spot in a game.

The backend locks the game row while checking player capacity:

```python
select(Game).where(
    Game.id == game_id
).with_for_update()
```

This helps prevent a game from exceeding its maximum number of players during concurrent join requests.

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
- Joining games
- Duplicate joins
- Leaving games
- Player count updates

Tests can be run with:

```bash
pytest -v
```

---

# What Rally Will Become

The long-term goal is to evolve Rally from a working full-stack application into a scalable, production-oriented backend system.

The project will progressively introduce better validation, performance improvements, distributed infrastructure, and measurable scalability.

---

## Phase 2 — Production Quality

The current focus is improving the quality and maintainability of the application.

Planned improvements include:

- Stronger request validation
- Improved error handling
- Pagination
- Game filtering
- Search
- Database indexes
- Query optimization
- Structured logging
- Better test coverage
- Seed and test data
- Cleaner service-layer architecture

Example future API requests:

```text
GET /games?page=1&page_size=20

GET /games?skill=intermediate

GET /games?format=6v6

GET /games?status=open
```

---

## Phase 3 — Scalability

After the application layer is stable, Rally will be expanded to support a more distributed architecture.

Planned technologies include:

- Redis
- Docker
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
             v
           Redis
             |
             v
        PostgreSQL
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

Example future performance documentation:

```text
Concurrent users: 500
Requests/second: 1,200
p95 latency: 120 ms
p99 latency: 190 ms
Error rate: 0.2%
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
Validation and optimization
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

The goal is not only to build a volleyball application, but to use Rally as a practical environment for learning and demonstrating full-stack development, backend engineering, database design, concurrency, testing, and scalable system design.
