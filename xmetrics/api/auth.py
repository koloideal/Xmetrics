from fastapi import APIRouter, Depends, Form, HTTPException, Response, status
from itsdangerous import URLSafeTimedSerializer

from xmetrics.api.deps import get_serializer, require_session
from xmetrics.core.config import Settings
from xmetrics.core.security import verify_password

router = APIRouter(tags=["auth"])


@router.post("/login")
async def login(
    response: Response,
    username: str = Form(),
    password: str = Form(),
    settings: Settings = Depends(Settings),
    serializer: URLSafeTimedSerializer = Depends(get_serializer),
) -> dict:
    if username != settings.admin_username or not verify_password(
        password, settings.admin_password
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = serializer.dumps({"username": username})
    response.set_cookie(
        key="fw_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.session_max_age,
    )
    return {"ok": True}


@router.post("/logout")
async def logout(response: Response, _: str = Depends(require_session)) -> dict:
    response.delete_cookie("fw_session")
    return {"ok": True}


@router.get("/me")
async def me(username: str = Depends(require_session)) -> dict:
    return {"username": username}
