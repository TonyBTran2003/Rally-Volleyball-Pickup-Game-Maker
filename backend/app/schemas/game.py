from datetime import date, time
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.user import SkillLevel


GameFormat = Literal[
    "2v2",
    "4v4",
    "6v6",
]


GameStatus = Literal[
    "open",
    "cancelled",
    "completed",
]


class GameCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=100,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
    )

    location: str = Field(
        min_length=3,
        max_length=255,
    )

    game_date: date
    start_time: time

    max_players: int = Field(
        ge=2,
        le=24,
    )

    skill_level: SkillLevel

    format: GameFormat = "6v6"


class GameUpdate(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
    )

    location: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    game_date: Optional[date] = None
    start_time: Optional[time] = None

    max_players: Optional[int] = Field(
        default=None,
        ge=2,
        le=24,
    )

    skill_level: Optional[SkillLevel] = None
    format: Optional[GameFormat] = None
    status: Optional[GameStatus] = None


class GameResponse(BaseModel):
    id: int
    creator_id: int
    title: str
    description: Optional[str]
    location: str
    game_date: date
    start_time: time
    max_players: int
    current_players: int
    skill_level: str
    format: str
    status: str