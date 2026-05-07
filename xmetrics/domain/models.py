from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class ClientSnapshot:
    date: date
    email: str
    inbound_id: int
    up: int
    down: int


@dataclass(frozen=True, slots=True)
class WeeklyTraffic:
    week: str        # "2026-W18"
    upload_gb: float
    download_gb: float
    total_gb: float


@dataclass(frozen=True, slots=True)
class ClientStat:
    email: str
    inbound_id: int
    upload_gb: float
    download_gb: float
    total_gb: float
    enabled: bool
