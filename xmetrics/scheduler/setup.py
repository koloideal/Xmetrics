import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dishka import AsyncContainer

from xmetrics.domain.interfaces import ISnapshotRepository, IXuiReader
from xmetrics.scheduler.sync_task import SyncTrafficUseCase

logger = logging.getLogger(__name__)


def _make_trigger(cron_expr: str) -> CronTrigger:
    parts = cron_expr.strip().split()
    minute, hour, day, month, dow = (parts + ["*"] * 5)[:5]
    return CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow)


class Scheduler:
    def __init__(self, container: AsyncContainer, cron_expr: str) -> None:
        self._container = container
        self._scheduler = AsyncIOScheduler()
        self._scheduler.add_job(
            self._job,
            _make_trigger(cron_expr),
            id="sync_traffic",
            replace_existing=True,
        )

    async def _job(self) -> None:
        async with self._container() as rc:
            reader = await rc.get(IXuiReader)
            repo = await rc.get(ISnapshotRepository)
            await SyncTrafficUseCase(reader, repo).execute()

    def start(self) -> None:
        self._scheduler.start()

    def stop(self) -> None:
        self._scheduler.shutdown(wait=False)

    def reschedule(self, cron_expr: str) -> None:
        self._scheduler.reschedule_job("sync_traffic", trigger=_make_trigger(cron_expr))
        logger.info("rescheduled sync to '%s'", cron_expr)