import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.toml"


@dataclass
class AppConfig:
    db_path: str
    secret_key: str
    history_weeks: int
    session_max_age: int


@dataclass
class AdminConfig:
    username: str
    password_hash: str


@dataclass
class XuiConfig:
    db_path: str
    sync_cron: str


@dataclass
class Settings:
    app: AppConfig
    admin: AdminConfig
    xui: XuiConfig
    _path: Path = field(default=CONFIG_PATH, repr=False, compare=False)

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> "Settings":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls(
            app=AppConfig(**data["app"]),
            admin=AdminConfig(**data["admin"]),
            xui=XuiConfig(**data["xui"]),
            _path=path,
        )

    def save(self) -> None:
        content = f"""[app]
db_path = {self.app.db_path!r}
secret_key = {self.app.secret_key!r}
history_weeks = {self.app.history_weeks}
session_max_age = {self.app.session_max_age}

[admin]
username = {self.admin.username!r}
password_hash = {self.admin.password_hash!r}

[xui]
db_path = {self.xui.db_path!r}
sync_cron = {self.xui.sync_cron!r}
"""
        self._path.write_text(content, encoding="utf-8")
