from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    admin_username: str
    admin_password: str
    xui_db_path: str
    app_db_path: str = "./xmetrics.db"
    sync_cron: str = "0 * * * *"
    history_weeks: int = 52
    session_max_age: int = 86400 * 7

    model_config = SettingsConfigDict(
        env_prefix="FLOWWATCH_",
        env_file=".env",
        env_file_encoding="utf-8",
    )
