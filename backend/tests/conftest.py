import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Game, GamePlayer, User


TEST_DATABASE_URL = (
    "postgresql+psycopg://"
    "rally_user:rally_dev_password"
    "@localhost:5432/rally_test"
)


test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)

def override_get_db():
    with TestingSessionLocal() as db:
        yield db

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)

def setup_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(autouse=True)
def clean_database():
    yield

    with test_engine.begin() as connection:
        for table in reversed(
            Base.metadata.sorted_tables
        ):
            connection.execute(
                table.delete()
            )

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Game, GamePlayer, User


TEST_DATABASE_URL = (
    "postgresql+psycopg://"
    "rally_user:rally_dev_password"
    "@localhost:5432/rally_test"
)


test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = (
    override_get_db
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_database():
    yield

    with test_engine.begin() as connection:
        for table in reversed(
            Base.metadata.sorted_tables
        ):
            connection.execute(
                table.delete()
            )


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    client.post(
        "/auth/register",
        json={
            "email": "tony@example.com",
            "username": "tony",
            "password": "RallyPass123!",
            "skill_level": "intermediate",
            "preferred_position": "setter",
        },
    )


    response = client.post(
        "/auth/login",
        data={
            "username": "tony",
            "password": "RallyPass123!",
        },
    )


    token = response.json()[
        "access_token"
    ]


    return {
        "Authorization":
            "Bearer {}".format(token)
    }