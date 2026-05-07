import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from xmetrics.domain.interfaces import ISnapshotRepository
from xmetrics.domain.models import ClientStat, ClientSnapshot, WeeklyTraffic
from xmetrics.infrastructure.db import SnapshotRow


class SnapshotRepository(ISnapshotRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session_factory

    async def save_snapshot(self, snapshot: ClientSnapshot) -> None:
        async with self._factory() as session:
            stmt = (
                insert(SnapshotRow)
                .values(
                    date=snapshot.date,
                    email=snapshot.email,
                    inbound_id=snapshot.inbound_id,
                    up=snapshot.up,
                    down=snapshot.down,
                )
                .on_conflict_do_update(
                    index_elements=["date", "email"],
                    set_={"up": snapshot.up, "down": snapshot.down},
                )
            )
            await session.execute(stmt)
            await session.commit()

    async def get_weekly_totals(self, since: datetime.date) -> list[WeeklyTraffic]:
        async with self._factory() as session:
            rows = (
                await session.execute(
                    select(SnapshotRow).where(SnapshotRow.date >= since).order_by(SnapshotRow.date)
                )
            ).scalars().all()

        # compute daily diff per email then group by iso-week
        from collections import defaultdict

        prev: dict[str, tuple[int, int]] = {}
        week_up: dict[str, int] = defaultdict(int)
        week_down: dict[str, int] = defaultdict(int)

        for row in rows:
            prev_up, prev_down = prev.get(row.email, (0, 0))
            diff_up = max(0, row.up - prev_up)
            diff_down = max(0, row.down - prev_down)
            prev[row.email] = (row.up, row.down)

            iso = row.date.isocalendar()
            label = f"{iso.year}-W{iso.week:02d}"
            week_up[label] += diff_up
            week_down[label] += diff_down

        result: list[WeeklyTraffic] = []
        for week in sorted(set(week_up) | set(week_down)):
            u = week_up[week] / 1024**3
            d = week_down[week] / 1024**3
            result.append(WeeklyTraffic(week=week, upload_gb=round(u, 3), download_gb=round(d, 3), total_gb=round(u + d, 3)))
        return result

    async def get_latest_client_stats(self) -> list[ClientStat]:
        async with self._factory() as session:
            subq = (
                select(SnapshotRow.email, func.max(SnapshotRow.date).label("max_date"))
                .group_by(SnapshotRow.email)
                .subquery()
            )
            rows = (
                await session.execute(
                    select(SnapshotRow).join(
                        subq,
                        (SnapshotRow.email == subq.c.email) & (SnapshotRow.date == subq.c.max_date),
                    )
                )
            ).scalars().all()

        return [
            ClientStat(
                email=r.email,
                inbound_id=r.inbound_id,
                upload_gb=round(r.up / 1024**3, 3),
                download_gb=round(r.down / 1024**3, 3),
                total_gb=round((r.up + r.down) / 1024**3, 3),
                enabled=True,
            )
            for r in sorted(rows, key=lambda x: x.up + x.down, reverse=True)
        ]
