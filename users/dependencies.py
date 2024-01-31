from fastapi import Depends, HTTPException, status

from auth.dependencies import get_current_auth_user
from models.role import Role
from users.schemas import UserSchema


def verify_admin_access(
    user: UserSchema = Depends(get_current_auth_user),
):
    if user.role == Role.ADMIN:
        return True
    return False


def verify_moderator_access(
    user: UserSchema = Depends(get_current_auth_user),
):
    if user.role == Role.MODERATOR:
        return True
    return False


def verify_admin_or_moderator_access(
    admin: bool = Depends(verify_admin_access),
    moderator: bool = Depends(verify_moderator_access),
):
    if admin or moderator:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this resource.",
    )
