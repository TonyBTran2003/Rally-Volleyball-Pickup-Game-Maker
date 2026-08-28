from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    game_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    max_players: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    skill_level: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    format: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="6v6",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
    Index(
        "ix_games_status_date_time",
        "status",
        "game_date",
        "start_time",
    ),
    Index(
        "ix_games_skill_level_date",
        "skill_level",
        "game_date",
    ),
)