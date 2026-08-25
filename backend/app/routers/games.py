from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app.models.game import Game
from app.models.game_player import GamePlayer
from app.models.user import User
from app.schemas.game import (
    GameCreate,
    GameResponse,
    GameUpdate,
)

from app.services import game_service

from app.services.game_service import (
    build_game_response,
    get_game_or_404,
    get_membership,
    get_player_count,
)


router = APIRouter(
    prefix="/games",
    tags=["games"],
)




@router.post(
    "",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
)

def create_game_endpoint(
    game_data: GameCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return game_service.create_game(
        game_data,
        current_user,
        db,
    )


@router.get(
    "",
    response_model=List[GameResponse],
)
def get_games(
    db: Session = Depends(get_db),
):
    return game_service.list_games(db)


@router.get(
    "/{game_id}",
    response_model=GameResponse,
)
def get_game(
    game_id: int,
    db: Session = Depends(get_db),
):
    game = get_game_or_404(
        game_id,
        db,
    )

    return build_game_response(
        game,
        db,
    )


@router.patch(
    "/{game_id}",
    response_model=GameResponse,
)
def update_game_endpoint(
    game_id: int,
    game_data: GameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return game_service.update_game(
        game_id,
        game_data,
        current_user,
        db,
    )


@router.delete(
    "/{game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_game_endpoint(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    game_service.delete_game(
        game_id,
        current_user,
        db,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    "/{game_id}/join",
    response_model=GameResponse,
)
def join_game_endpoint(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return game_service.join_game(
        game_id,
        current_user,
        db,
    )


@router.delete(
    "/{game_id}/leave",
    response_model=GameResponse,
)
def leave_game_endpoint(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return game_service.leave_game(
        game_id,
        current_user,
        db,
    )