from fastapi import HTTPException, status
from models import User, Role


def require_role(
    user: User,
    required_role: Role,
):
    if user.role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You must be a {required_role} to access this resource.",
        )


def ensure_user_exists(user: User):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
