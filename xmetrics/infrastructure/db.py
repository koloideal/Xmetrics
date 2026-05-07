import datetime
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SnapshotRow(Base):
    __tablename__ = "snapshots"
    __table_args__ = (UniqueConstraint("date", "email", name="uq_snapshot_date_email"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(nullable=False, index=True)
    email: Mapped[str] = mapped_column(nullable=False)
    inbound_id: Mapped[int] = mapped_column(nullable=False)
    up: Mapped[int] = mapped_column(nullable=False, default=0)
    down: Mapped[int] = mapped_column(nullable=False, default=0)


def make_engine(db_path: str) -> AsyncEngine:
    return create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)


def make_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
