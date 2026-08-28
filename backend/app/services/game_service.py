from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.game import Game
from app.models.game_player import GamePlayer
from app.schemas.game import GameResponse

from app.models.user import User
from app.schemas.game import GameCreate

from app.schemas.game import GameResponse, GameUpdate

from datetime import date


def validate_required_text(
    value: str,
    field_name: str,
):
    if not value.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="{} cannot be blank".format(
                field_name
            ),
        )


def validate_game_date(
    game_date: date,
):
    if game_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game date cannot be in the past",
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
        .where(
            GamePlayer.game_id == game_id
        )
    )

    return db.scalar(statement)


def get_membership(
    game_id: int,
    user_id: int,
    db: Session,
):
    statement = select(
        GamePlayer
    ).where(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == user_id,
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


def create_game(
    game_data: GameCreate,
    current_user: User,
    db: Session,
):
    
    validate_game_date(game_data.game_date)
    validate_required_text(game_data.title,"Title",)
    validate_required_text(game_data.location, "Location",)
    game = Game(
    creator_id=current_user.id,
    title=game_data.title.strip(),
    description=(
        game_data.description.strip()
        if game_data.description
        else None
    ),
    location=game_data.location.strip(),
    game_date=game_data.game_date,
    start_time=game_data.start_time,
    max_players=game_data.max_players,
    skill_level=game_data.skill_level,
    format=game_data.format,
    status="open",
)

    db.add(game)

    db.flush()

    membership = GamePlayer(
        game_id=game.id,
        user_id=current_user.id,
    )

    db.add(membership)

    db.commit()
    db.refresh(game)

    return build_game_response(
        game,
        db,
    )


def list_games(
    db: Session,
):
    statement = (
        select(Game)
        .order_by(
            Game.game_date,
            Game.start_time,
        )
    )

    games = db.scalars(
        statement
    ).all()

    return [
        build_game_response(
            game,
            db,
        )
        for game in games
    ]


def join_game(
    game_id: int,
    current_user: User,
    db: Session,
):
    statement = (
        select(Game)
        .where(Game.id == game_id)
        .with_for_update()
    )

    game = db.scalar(statement)

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

    membership = get_membership(
        game.id,
        current_user.id,
        db,
    )

    if membership:
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


def leave_game(
    game_id: int,
    current_user: User,
    db: Session,
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
            detail=(
                "Game creators cannot leave "
                "their own game"
            ),
        )

    db.delete(membership)
    db.commit()

    return build_game_response(
        game,
        db,
    )


def update_game(
    game_id: int,
    game_data: GameUpdate,
    current_user: User,
    db: Session,
):
    game = get_game_or_404(
        game_id,
        db,
    )

    if game.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not allowed "
                "to update this game"
            ),
        )

    update_data = game_data.model_dump(
        exclude_unset=True
    )

    current_players = get_player_count(
        game.id,
        db,
    )

    if "max_players" in update_data:
        if (
            update_data["max_players"]
            < current_players
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_409_CONFLICT
                ),
                detail=(
                    "Maximum players cannot "
                    "be lower than the current "
                    "player count"
                ),
            )

    if "game_date" in update_data:
        validate_game_date(
            update_data["game_date"]
        )

    if "title" in update_data:
        validate_required_text(
            update_data["title"],
            "Title",
        )

        update_data["title"] = (
            update_data["title"].strip()
        )

    if "location" in update_data:
        validate_required_text(
            update_data["location"],
            "Location",
        )

        update_data["location"] = (
            update_data[
                "location"
            ].strip()
        )

    if (
        "description" in update_data
        and update_data["description"]
    ):
        update_data["description"] = (
            update_data[
                "description"
            ].strip()
        )

    for field, value in update_data.items():
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


def delete_game(
    game_id: int,
    current_user: User,
    db: Session,
):
    game = get_game_or_404(
        game_id,
        db,
    )

    if game.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this game",
        )

    db.delete(game)
    db.commit()