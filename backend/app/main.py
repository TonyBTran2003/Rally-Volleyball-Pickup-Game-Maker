from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Game, GamePlayer, User
from app.routers import auth, games, users

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Rally API",
    description="API for organizing and finding volleyball games",
    version="0.1.0",
)

allowed_origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(games.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Rally"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT current_database(), current_user")
    ).one()

    return {
        "status": "healthy",
        "database": result[0],
        "user": result[1],
    }