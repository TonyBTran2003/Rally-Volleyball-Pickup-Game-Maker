from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


SkillLevel = Literal[
    "beginner",
    "intermediate",
    "advanced",
    "competitive",
]

Position = Literal[
    "setter",
    "outside",
    "opposite",
    "middle",
    "libero",
    "ds",
    "any",
]


class UserCreate(BaseModel):
    email: EmailStr

    username: str = Field(
        min_length=3,
        max_length=50,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    skill_level: Optional[SkillLevel] = None
    preferred_position: Optional[Position] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    skill_level: Optional[str] = None
    preferred_position: Optional[str] = None # no password so the user never gets back a password or password hash