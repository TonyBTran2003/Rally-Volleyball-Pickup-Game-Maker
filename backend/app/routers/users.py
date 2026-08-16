from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.game_player import GamePlayer
from app.models.user import User
from app.schemas.user import UserResponse


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        skill_level=current_user.skill_level,
        preferred_position=current_user.preferred_position,
    )


@router.get(
    "/me/games",
    response_model=List[int],
)
def get_my_games(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = select(
        GamePlayer.game_id
    ).where(
        GamePlayer.user_id == current_user.id
    )

    game_ids = db.scalars(statement).all()

    return list(game_ids)