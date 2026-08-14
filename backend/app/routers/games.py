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


router = APIRouter(
    prefix="/games",
    tags=["games"],
)


def get_game_or_404(
    game_id: int,
    db: Session,
):
    game = db.get(Game, game_id)

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    return game


def get_player_count(
    game_id: int,
    db: Session,
):
    statement = (
        select(func.count())
        .select_from(GamePlayer)
        .where(GamePlayer.game_id == game_id)
    )

    return db.scalar(statement)


def build_game_response(
    game: Game,
    db: Session,
):
    return GameResponse(
        id=game.id,
        creator_id=game.creator_id,
        title=game.title,
        description=game.description,
        location=game.location,
        game_date=game.game_date,
        start_time=game.start_time,
        max_players=game.max_players,
        current_players=get_player_count(
            game.id,
            db,
        ),
        skill_level=game.skill_level,
        format=game.format,
        status=game.status,
    )


def get_membership(
    game_id: int,
    user_id: int,
    db: Session,
):
    statement = select(GamePlayer).where(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == user_id,
    )

    return db.scalar(statement)


@router.post(
    "",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_game(
    game_data: GameCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    game = Game(
        creator_id=current_user.id,
        title=game_data.title,
        description=game_data.description,
        location=game_data.location,
        game_date=game_data.game_date,
        start_time=game_data.start_time,
        max_players=game_data.max_players,
        skill_level=game_data.skill_level,
        format=game_data.format,
        status="open",
    )

    db.add(game)

    db.flush()

    creator_membership = GamePlayer(
        game_id=game.id,
        user_id=current_user.id,
    )

    db.add(creator_membership)

    db.commit()
    db.refresh(game)

    return build_game_response(
        game,
        db,
    )


@router.get(
    "",
    response_model=List[GameResponse]
)
def get_games(
    db: Session = Depends(get_db),
):
    statement = (
        select(Game)
        .order_by(
            Game.game_date,
            Game.start_time,
        )
    )

    games = db.scalars(statement).all()

    return [
        build_game_response(game, db)
        for game in games
    ]


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
def update_game(
    game_id: int,
    game_data: GameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    game = get_game_or_404(
        game_id,
        db,
    )

    if game.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this game",
        )

    updates = game_data.model_dump(
        exclude_unset=True
    )

    for field, value in updates.items():
        setattr(
            game,
            field,
            value,
        )

    db.commit()
    db.refresh(game)

    return build_game_response(
        game,
        db,
    )


@router.delete(
    "/{game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    game = get_game_or_404(
        game_id,
        db,
    )

    if game.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this game",
        )

    db.delete(game)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    "/{game_id}/join",
    response_model=GameResponse,
)
def join_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    game_statement = (
        select(Game)
        .where(Game.id == game_id)
        .with_for_update()
    )

    game = db.scalar(game_statement)

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    if game.status != "open":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This game is not open for joining",
        )

    existing_membership = get_membership(
        game.id,
        current_user.id,
        db,
    )

    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already joined this game",
        )

    current_players = get_player_count(
        game.id,
        db,
    )

    if current_players >= game.max_players:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This game is full",
        )

    membership = GamePlayer(
        game_id=game.id,
        user_id=current_user.id,
    )

    db.add(membership)
    db.commit()

    return build_game_response(
        game,
        db,
    )


@router.delete( #creator cant leave the game. delete or cancel game
    "/{game_id}/leave",
    response_model=GameResponse,
)
def leave_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    game = get_game_or_404(
        game_id,
        db,
    )

    membership = get_membership(
        game.id,
        current_user.id,
        db,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have not joined this game",
        )

    if game.creator_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Game creators cannot leave their own game",
        )

    db.delete(membership)
    db.commit()

    return build_game_response(
        game,
        db,
    )