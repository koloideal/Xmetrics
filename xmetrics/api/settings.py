from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator

from xmetrics.api.deps import require_session
from xmetrics.core.config import Settings
from xmetrics.core.security import hash_password, verify_password
from xmetrics.scheduler.setup import reschedule

router = APIRouter(prefix="/api/settings", tags=["settings"], route_class=DishkaRoute)


class XuiSettingsIn(BaseModel):
    db_path: str
    sync_cron: str

    @field_validator("sync_cron")
    @classmethod
    def valid_cron(cls, v: str) -> str:
        parts = v.strip().split()
        if len(parts) != 5:
            raise ValueError("Cron должен содержать ровно 5 полей")
        return v.strip()


class PasswordChangeIn(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Минимум 8 символов")
        return v


class SettingsOut(BaseModel):
    xui_db_path: str
    sync_cron: str
    history_weeks: int
    admin_username: str


@router.get("", response_model=SettingsOut)
async def get_settings(
    _: Annotated[str, Depends(require_session)],
    settings: FromDishka[Settings],
) -> SettingsOut:
    return SettingsOut(
        xui_db_path=settings.xui.db_path,
        sync_cron=settings.xui.sync_cron,
        history_weeks=settings.app.history_weeks,
        admin_username=settings.admin.username,
    )


@router.put("/xui")
async def update_xui(
    _: Annotated[str, Depends(require_session)],
    settings: FromDishka[Settings],
    body: XuiSettingsIn,
) -> dict:
    settings.xui.db_path = body.db_path
    settings.xui.sync_cron = body.sync_cron
    settings.save()
    reschedule(body.sync_cron)
    return {"ok": True}


@router.put("/password")
async def change_password(
    username: Annotated[str, Depends(require_session)],
    settings: FromDishka[Settings],
    body: PasswordChangeIn,
) -> dict:
    if not verify_password(body.current_password, settings.admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный текущий пароль"
        )
    settings.admin.password_hash = hash_password(body.new_password)
    settings.save()
    return {"ok": True}
