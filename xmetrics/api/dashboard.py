import datetime

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from xmetrics.api.deps import require_session
from xmetrics.core.config import Settings
from xmetrics.domain.interfaces import ISnapshotRepository
from xmetrics.domain.models import ClientStat, WeeklyTraffic
from xmetrics.scheduler.sync_task import SyncTrafficUseCase
from xmetrics.domain.interfaces import IXuiReader

router = APIRouter(tags=["dashboard"])


@router.get("/api/weekly")
@inject
async def weekly(
    weeks: int = 16,
    _: str = Depends(require_session),
    repo: ISnapshotRepository = FromDishka(),
    settings: Settings = FromDishka(),
) -> list[WeeklyTraffic]:
    since = datetime.date.today() - datetime.timedelta(weeks=min(weeks, settings.history_weeks))
    return await repo.get_weekly_totals(since)


@router.get("/api/clients")
@inject
async def clients(
    _: str = Depends(require_session),
    repo: ISnapshotRepository = FromDishka(),
) -> list[ClientStat]:
    return await repo.get_latest_client_stats()


@router.post("/api/sync")
@inject
async def manual_sync(
    _: str = Depends(require_session),
    reader: IXuiReader = FromDishka(),
    repo: ISnapshotRepository = FromDishka(),
) -> dict:
    count = await SyncTrafficUseCase(reader, repo).execute()
    return {"synced": count}
