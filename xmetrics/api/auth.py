from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Form, HTTPException, Response, status
from itsdangerous import URLSafeTimedSerializer

from xmetrics.api.deps import require_session
from xmetrics.core.config import Settings
from xmetrics.core.security import verify_password

router = APIRouter(tags=["auth"])


@router.post("/login")
@inject
async def login(
    response: Response,
    settings: FromDishka[Settings],
    username: str = Form(),
    password: str = Form()
) -> dict:
    if username != settings.admin.username or not verify_password(
        password, settings.admin.password_hash
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    s = URLSafeTimedSerializer(settings.app.secret_key)
    token = s.dumps({"username": username})
    response.set_cookie(
        key="fw_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.app.session_max_age,
    )
    return {"ok": True}


@router.post("/logout")
async def logout(response: Response, _: str = Depends(require_session)) -> dict:
    response.delete_cookie("fw_session")
    return {"ok": True}


@router.get("/me")
async def me(username: str = Depends(require_session)) -> dict:
    return {"username": username}