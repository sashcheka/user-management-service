from fastapi import APIRouter, Body

from .temp_models import UserCreate
from .utils import *

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup/")
def signup(user: UserSignup):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user.password = hash_password(user.password)

    fake_users_db[user.username] = UserLogin(
        username=user.username, password=user.password
    )
    return {"user": user, "message": f"User {user.username} created successfully."}


@router.post("/login/")
def auth_user_issue_jwt(user: UserLogin = Depends(validate_auth_user)):
    user = UserCreate(**user.model_dump())
    payload = {
        "sub": user.id,
        "username": user.username,
        "email": user.email,
    }

    access_token = create_access_token(payload=payload)
    refresh_token = create_refresh_token(payload=payload)

    redis_client.setex(refresh_token, REFRESH_TOKEN_EXPIRE_MINUTES * 60, "valid")

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh-token/")
def refresh_token(refresh_token_in: str = Body(...)):
    payload = verify_refresh_token(refresh_token_in)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token or blacklisted",
        )
    access_token = create_access_token(payload=payload)
    new_refresh_token = create_refresh_token(payload=payload)

    redis_client.setex(new_refresh_token, REFRESH_TOKEN_EXPIRE_MINUTES * 60, "valid")

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": new_refresh_token,
    }


@router.get("/users/me/")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserLogin = Depends(get_current_active_auth_user),
):
    iat = payload.get("iat")
    return {
        "username": user.username,
        "logged_in_at": iat,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
