import datetime
import random
import sqlite3
from pathlib import Path

DB_PATH = Path("xmetrics.db")

CLIENTS = [
    ("alice@vpn",   1),
    ("bob@vpn",     1),
    ("charlie@vpn", 2),
    ("diana@vpn",   2),
    ("eve@vpn",     3),
]

WEEKS = 24

CREATE_SNAPSHOTS = """
CREATE TABLE IF NOT EXISTS snapshots (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    date       TEXT    NOT NULL,
    email      TEXT    NOT NULL,
    inbound_id INTEGER NOT NULL,
    up         INTEGER NOT NULL DEFAULT 0,
    down       INTEGER NOT NULL DEFAULT 0,
    UNIQUE(date, email)
)
"""


def iso_week(d: datetime.date) -> str:
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def seed():
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Удалена старая {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute(CREATE_SNAPSHOTS)

    today = datetime.date.today()
    start = today - datetime.timedelta(weeks=WEEKS)

    rows = []
    for email, inbound_id in CLIENTS:
        # у каждого клиента свой базовый уровень трафика
        base_up_daily   = random.randint(300, 800) * 1024**2   # 300–800 MB/day
        base_down_daily = random.randint(1, 5) * 1024**3       # 1–5 GB/day

        # накопленные счётчики (как в 3x-ui — только растут)
        cum_up   = random.randint(0, 10) * 1024**3
        cum_down = random.randint(0, 30) * 1024**3

        d = start
        while d <= today:
            # небольшой дневной шум + недельная синусоида
            day_factor = 0.5 + 0.5 * abs(random.gauss(1.0, 0.35))
            week_factor = 1.0 + 0.3 * abs(datetime.date(d.year, d.month, d.day).weekday() / 6 - 0.5)

            cum_up   += int(base_up_daily   * day_factor * week_factor)
            cum_down += int(base_down_daily * day_factor * week_factor)

            rows.append((d.isoformat(), email, inbound_id, cum_up, cum_down))
            d += datetime.timedelta(days=1)

    conn.executemany(
        "INSERT OR REPLACE INTO snapshots (date, email, inbound_id, up, down) VALUES (?,?,?,?,?)",
        rows,
    )
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    conn.close()

    print(f"БД создана: {DB_PATH.resolve()}")
    print(f"Строк в snapshots: {count}")
    print(f"Клиентов: {len(CLIENTS)}, недель: {WEEKS}, дней на клиента: {WEEKS * 7}")
    print()
    print("Пример данных (последние 3 дня, alice@vpn):")
    conn2 = sqlite3.connect(DB_PATH)
    for row in conn2.execute(
        "SELECT date, up, down FROM snapshots WHERE email='alice@vpn' ORDER BY date DESC LIMIT 3"
    ):
        up_gb   = row[1] / 1024**3
        down_gb = row[2] / 1024**3
        print(f"  {row[0]}  up={up_gb:.2f} GB  down={down_gb:.2f} GB")
    conn2.close()


if __name__ == "__main__":
    seed()