from datetime import date, time, timedelta

from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.game import Game
from app.models.game_player import GamePlayer
from app.models.user import User


DEMO_PASSWORD = "DemoPass123!"


def get_or_create_user(
    db,
    email,
    username,
    skill_level,
    preferred_position,
):
    user = db.scalar(
        select(User).where(
            User.username == username
        )
    )

    if user:
        return user

    user = User(
        email=email,
        username=username,
        password_hash=hash_password(
            DEMO_PASSWORD
        ),
        skill_level=skill_level,
        preferred_position=preferred_position,
    )

    db.add(user)
    db.flush()

    return user


def get_or_create_game(
    db,
    creator,
    title,
    description,
    location,
    days_from_now,
    start_time,
    max_players,
    skill_level,
    game_format,
):
    game = db.scalar(
        select(Game).where(
            Game.title == title
        )
    )

    if game:
        return game

    game = Game(
        creator_id=creator.id,
        title=title,
        description=description,
        location=location,
        game_date=(
            date.today()
            + timedelta(days=days_from_now)
        ),
        start_time=start_time,
        max_players=max_players,
        skill_level=skill_level,
        format=game_format,
        status="open",
    )

    db.add(game)
    db.flush()

    return game


def add_player(
    db,
    game,
    user,
):
    membership = db.scalar(
        select(GamePlayer).where(
            GamePlayer.game_id == game.id,
            GamePlayer.user_id == user.id,
        )
    )

    if membership:
        return

    db.add(
        GamePlayer(
            game_id=game.id,
            user_id=user.id,
        )
    )


def seed():
    with SessionLocal() as db:
        tony = get_or_create_user(
            db,
            "tony.demo@example.com",
            "tony_demo",
            "intermediate",
            "setter",
        )

        alex = get_or_create_user(
            db,
            "alex.demo@example.com",
            "alex_demo",
            "advanced",
            "outside",
        )

        sam = get_or_create_user(
            db,
            "sam.demo@example.com",
            "sam_demo",
            "beginner",
            "middle",
        )

        jordan = get_or_create_user(
            db,
            "jordan.demo@example.com",
            "jordan_demo",
            "competitive",
            "libero",
        )

        casey = get_or_create_user(
            db,
            "casey.demo@example.com",
            "casey_demo",
            "intermediate",
            "opposite",
        )

        friday = get_or_create_game(
            db,
            tony,
            "Friday Night Volleyball",
            "Intermediate 6v6 pickup.",
            "Main Recreation Center",
            2,
            time(18, 30),
            12,
            "intermediate",
            "6v6",
        )

        beach = get_or_create_game(
            db,
            alex,
            "Saturday Beach Doubles",
            "Competitive beach doubles.",
            "Mission Beach",
            3,
            time(10, 0),
            4,
            "advanced",
            "2v2",
        )

        beginners = get_or_create_game(
            db,
            sam,
            "Beginner Open Gym",
            "Beginner-friendly pickup volleyball.",
            "Community Gym",
            4,
            time(17, 0),
            12,
            "beginner",
            "6v6",
        )

        competitive = get_or_create_game(
            db,
            jordan,
            "Competitive Sixes",
            "Fast-paced competitive 6v6.",
            "Sports Arena",
            5,
            time(19, 0),
            12,
            "competitive",
            "6v6",
        )

        fours = get_or_create_game(
            db,
            casey,
            "Sunday 4v4",
            "Intermediate four-player teams.",
            "Northside Courts",
            6,
            time(15, 0),
            8,
            "intermediate",
            "4v4",
        )

        late_night = get_or_create_game(
            db,
            tony,
            "Late Night Open Gym",
            "Casual evening volleyball.",
            "University Recreation Center",
            7,
            time(20, 30),
            12,
            "intermediate",
            "6v6",
        )

        # Creators are members of their own games.
        add_player(db, friday, tony)
        add_player(db, beach, alex)
        add_player(db, beginners, sam)
        add_player(db, competitive, jordan)
        add_player(db, fours, casey)
        add_player(db, late_night, tony)

        # Add additional players.
        add_player(db, friday, alex)
        add_player(db, friday, casey)

        add_player(db, beach, jordan)

        add_player(db, beginners, tony)
        add_player(db, beginners, casey)

        add_player(db, competitive, alex)
        add_player(db, competitive, casey)

        add_player(db, fours, tony)
        add_player(db, fours, alex)
        add_player(db, fours, sam)

        db.commit()

        print("Rally demo data seeded successfully.")
        print(
            "Demo password: {}".format(
                DEMO_PASSWORD
            )
        )


if __name__ == "__main__":
    seed()