from functools import lru_cache

from fastapi import Cookie, Depends, HTTPException, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from xmetrics.core.config import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.load()


async def require_session(
    session: str | None = Cookie(default=None, alias="fw_session"),
    settings: Settings = Depends(get_settings),
) -> str:
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    s = URLSafeTimedSerializer(settings.app.secret_key)
    try:
        data = s.loads(session, max_age=settings.app.session_max_age)
    except (SignatureExpired, BadSignature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return data["username"]
