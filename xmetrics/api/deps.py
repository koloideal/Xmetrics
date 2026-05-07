from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Cookie, Depends, HTTPException, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from xmetrics.core.config import Settings


async def require_session(
    session: str | None = Cookie(default=None, alias="fw_session"),
    settings: Settings = Depends(lambda: None),   # overridden below
) -> str:
    raise NotImplementedError


def make_require_session():
    @inject
    async def _guard(
        settings: FromDishka[Settings],
        session: str | None = Cookie(default=None, alias="fw_session"),
    ) -> str:
        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        s = URLSafeTimedSerializer(settings.app.secret_key)
        try:
            data = s.loads(session, max_age=settings.app.session_max_age)
        except (SignatureExpired, BadSignature):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return data["username"]
    return _guard


require_session = make_require_session()