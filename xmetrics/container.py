from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from xmetrics.core.config import Settings
from xmetrics.domain.interfaces import ISnapshotRepository, IXuiReader
from xmetrics.infrastructure.db import make_engine, make_session_factory
from xmetrics.infrastructure.repository import SnapshotRepository
from xmetrics.infrastructure.xui_reader import XuiSqliteReader


class AppProvider(Provider):
    scope = Scope.APP

    @provide
    def settings(self) -> Settings:
        return Settings()

    @provide
    def engine(self, settings: Settings) -> AsyncEngine:
        return make_engine(settings.app_db_path)

    @provide
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return make_session_factory(engine)

    @provide
    def snapshot_repository(self, sf: async_sessionmaker[AsyncSession]) -> ISnapshotRepository:
        return SnapshotRepository(sf)

    @provide
    def xui_reader(self, settings: Settings) -> IXuiReader:
        return XuiSqliteReader(settings.xui_db_path)
