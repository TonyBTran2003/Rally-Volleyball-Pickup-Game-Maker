from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
)

from sqlalchemy.exc import IntegrityError


def register_user(
    user_data: UserCreate,
    db: Session,
):
    email = user_data.email.lower()
    username = user_data.username.strip().lower()

    existing_email = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    existing_username = db.scalar(
        select(User).where(
            User.username == username
        )
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    user = User(
        email=email,
        username=username,
        password_hash=hash_password(
            user_data.password
        ),
        skill_level=user_data.skill_level,
        preferred_position=(
            user_data.preferred_position
        ),
    )

    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Email or username "
                "already exists"
            ),
        )
    db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        skill_level=user.skill_level,
        preferred_position=(
            user.preferred_position
        ),
    )


def authenticate_user(
    username: str,
    password: str,
    db: Session,
):
    normalized_username = (
        username.strip().lower()
    )

    user = db.scalar(
        select(User).where(
            User.username
            == normalized_username
        )
    )

    if (
        user is None
        or not verify_password(
            password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Incorrect username or password"
            ),
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    return user