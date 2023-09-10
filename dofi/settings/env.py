from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{ROOT_DIR}/.env",
        env_file_encoding="utf-8",
    )

    # API tokens
    GITHUB_PAT: str | None = None
    # Database
    SQLITE_DB_PATH: Path


@lru_cache(maxsize=1)
def get_env_settings() -> EnvSettings:
    return EnvSettings()
