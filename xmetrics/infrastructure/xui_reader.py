import logging
import datetime
from pathlib import Path

import aiosqlite

from xmetrics.domain.interfaces import IXuiReader
from xmetrics.domain.models import ClientSnapshot

logger = logging.getLogger(__name__)


class XuiSqliteReader(IXuiReader):
    def __init__(self, db_path: str) -> None:
        self._path = db_path

    async def read_snapshots(self) -> list[ClientSnapshot]:
        if not Path(self._path).exists():
            logger.warning("x-ui db not found at '%s', skipping sync", self._path)
            return []

        today = datetime.date.today()
        try:
            async with aiosqlite.connect(self._path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(
                    "SELECT email, inbound_id, up, down FROM client_traffics"
                ) as cur:
                    rows = await cur.fetchall()
            return [
                ClientSnapshot(
                    date=today,
                    email=row["email"],
                    inbound_id=row["inbound_id"],
                    up=row["up"],
                    down=row["down"],
                )
                for row in rows
            ]
        except Exception as exc:
            logger.error("failed to read x-ui db: %s", exc)
            return []