import datetime
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends

from xmetrics.api.deps import require_session
from xmetrics.core.config import Settings
from xmetrics.domain.interfaces import ISnapshotRepository, IXuiReader
from xmetrics.domain.models import ClientStat, WeeklyTraffic
from xmetrics.scheduler.sync_task import SyncTrafficUseCase

router = APIRouter(tags=["dashboard"], route_class=DishkaRoute)


@router.get("/api/weekly")
async def weekly(
    _: Annotated[str, Depends(require_session)],
    repo: FromDishka[ISnapshotRepository],
    settings: FromDishka[Settings],
    weeks: int = 16,
) -> list[WeeklyTraffic]:
    since = datetime.date.today() - datetime.timedelta(weeks=min(weeks, settings.app.history_weeks))
    return await repo.get_weekly_totals(since)


@router.get("/api/clients")
async def clients(
    _: Annotated[str, Depends(require_session)],
    repo: FromDishka[ISnapshotRepository],
) -> list[ClientStat]:
    return await repo.get_latest_client_stats()


@router.post("/api/sync")
async def manual_sync(
    _: Annotated[str, Depends(require_session)],
    reader: FromDishka[IXuiReader],
    repo: FromDishka[ISnapshotRepository],
) -> dict:
    count = await SyncTrafficUseCase(reader, repo).execute()
    return {"synced": count}
