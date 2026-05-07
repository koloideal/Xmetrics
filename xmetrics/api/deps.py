from fastapi import Cookie, Depends, HTTPException, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from xmetrics.core.config import Settings


def get_serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key)


def require_session(
    session: str | None = Cookie(default=None, alias="fw_session"),
    settings: Settings = Depends(Settings),
) -> str:
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    s = URLSafeTimedSerializer(settings.secret_key)
    try:
        data = s.loads(session, max_age=settings.session_max_age)
    except (SignatureExpired, BadSignature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return data["username"]
