from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
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