import logging

from xmetrics.domain.interfaces import ISnapshotRepository, IXuiReader

logger = logging.getLogger(__name__)


class SyncTrafficUseCase:
    def __init__(self, reader: IXuiReader, repo: ISnapshotRepository) -> None:
        self._reader = reader
        self._repo = repo

    async def execute(self) -> int:
        snapshots = await self._reader.read_snapshots()
        for snap in snapshots:
            await self._repo.save_snapshot(snap)
        logger.info("sync done: %d clients saved", len(snapshots))
        return len(snapshots)
