from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db


app = FastAPI(
    title="Rally API",
    description="API for organizing and finding volleyball games",
    version="0.1.0",
)


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