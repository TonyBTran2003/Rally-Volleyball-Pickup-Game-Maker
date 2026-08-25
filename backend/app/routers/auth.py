from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.database import get_db
from app.schemas.auth import Token
from app.schemas.user import (
    UserCreate,
    UserResponse,
)
from app.services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    return auth_service.register_user(
        user_data,
        db,
    )


@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(
        form_data.username,
        form_data.password,
        db,
    )

    access_token = create_access_token(
        user.id
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )