import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dishka import AsyncContainer

from xmetrics.domain.interfaces import ISnapshotRepository, IXuiReader
from xmetrics.scheduler.sync_task import SyncTrafficUseCase

logger = logging.getLogger(__name__)


def build_scheduler(container: AsyncContainer, cron_expr: str) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    async def _job() -> None:
        async with container() as request_container:
            reader = await request_container.get(IXuiReader)
            repo = await request_container.get(ISnapshotRepository)
            await SyncTrafficUseCase(reader, repo).execute()

    parts = cron_expr.strip().split()
    minute, hour, day, month, day_of_week = (parts + ["*", "*", "*", "*", "*"])[:5]
    trigger = CronTrigger(
        minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week
    )
    scheduler.add_job(_job, trigger, id="sync_traffic", replace_existing=True)
    return scheduler
