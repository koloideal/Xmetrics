from abc import ABC, abstractmethod
from datetime import date

from xmetrics.domain.models import ClientSnapshot, ClientStat, WeeklyTraffic


class IXuiReader(ABC):
    @abstractmethod
    async def read_snapshots(self) -> list[ClientSnapshot]: ...


class ISnapshotRepository(ABC):
    @abstractmethod
    async def save_snapshot(self, snapshot: ClientSnapshot) -> None: ...

    @abstractmethod
    async def get_weekly_totals(self, since: date) -> list[WeeklyTraffic]: ...

    @abstractmethod
    async def get_latest_client_stats(self) -> list[ClientStat]: ...
