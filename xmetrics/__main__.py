import logging
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from xmetrics.api.auth import router as auth_router
from xmetrics.api.dashboard import router as dashboard_router
from xmetrics.api.settings_router import router as settings_router
from xmetrics.container import AppProvider
from xmetrics.core.config import Settings
from xmetrics.core.security import hash_password
from xmetrics.infrastructure.db import Base, make_engine
from xmetrics.scheduler.setup import build_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


def _bootstrap_password(settings: Settings) -> None:
    if settings.admin.password_hash:
        return
    generated = secrets.token_urlsafe(16)
    settings.admin.password_hash = hash_password(generated)
    settings.save()
    logger.warning("=" * 60)
    logger.warning("Первый старт. Временный пароль: %s", generated)
    logger.warning("Смените его в дашборде → Settings → Пароль")
    logger.warning("=" * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = app.state.dishka_container
    settings = await container.get(Settings)

    _bootstrap_password(settings)

    engine = make_engine("./flowwatch.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

    scheduler = build_scheduler(container, settings.xui.sync_cron)
    scheduler.start()
    logger.info("scheduler started: '%s'", settings.xui.sync_cron)

    yield

    scheduler.shutdown(wait=False)
    await container.close()


def create_app() -> FastAPI:
    app = FastAPI(title="Flowwatch", lifespan=lifespan)

    container = make_async_container(AppProvider(), FastapiProvider())
    setup_dishka(container, app)

    app.include_router(auth_router, prefix="/auth")
    app.include_router(dashboard_router)
    app.include_router(settings_router)

    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return app


app = create_app()