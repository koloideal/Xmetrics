from abc import ABC, abstractmethod
from datetime import date

from xmetrics.domain.models import ClientSnapshot, ClientStat, DailyTraffic, WeeklyTraffic


class IXuiReader(ABC):
    @abstractmethod
    async def read_snapshots(self) -> list[ClientSnapshot]: ...


class ISnapshotRepository(ABC):
    @abstractmethod
    async def save_snapshots(self, snapshots: list[ClientSnapshot]) -> int: ...

    @abstractmethod
    async def get_weekly_totals(self, since: date) -> list[WeeklyTraffic]: ...

    @abstractmethod
    async def get_daily_totals(self, since: date) -> list[DailyTraffic]: ...

    @abstractmethod
    async def get_latest_client_stats(self) -> list[ClientStat]: ...
