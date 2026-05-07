import datetime

import aiosqlite

from xmetrics.domain.interfaces import IXuiReader
from xmetrics.domain.models import ClientSnapshot


class XuiSqliteReader(IXuiReader):
    def __init__(self, xui_db_path: str) -> None:
        self._path = xui_db_path

    async def read_snapshots(self) -> list[ClientSnapshot]:
        today = datetime.date.today()
        async with aiosqlite.connect(self._path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT inbound_id, email, up, down FROM client_traffics WHERE enable = 1"
            ) as cursor:
                rows = await cursor.fetchall()

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
