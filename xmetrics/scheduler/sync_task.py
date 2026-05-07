import logging

from xmetrics.domain.interfaces import ISnapshotRepository, IXuiReader

logger = logging.getLogger(__name__)


class SyncTrafficUseCase:
    def __init__(self, reader: IXuiReader, repo: ISnapshotRepository) -> None:
        self._reader = reader
        self._repo = repo

    async def execute(self) -> int:
        snapshots = await self._reader.read_snapshots()
        if not snapshots:
            logger.warning("sync: no snapshots read, skipping write")
            return 0
        count = await self._repo.save_snapshots(snapshots)
        logger.info("sync: saved %d snapshots", count)
        return count