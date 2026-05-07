from sqlalchemy import Column, Date, Integer, String, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class SnapshotRow(Base):
    __tablename__ = "snapshots"
    __table_args__ = (UniqueConstraint("date", "email", name="uq_snapshot_date_email"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    email = Column(String, nullable=False)
    inbound_id = Column(Integer, nullable=False)
    up = Column(Integer, nullable=False, default=0)
    down = Column(Integer, nullable=False, default=0)


def make_engine(db_path: str) -> AsyncEngine:
    return create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)


def make_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
