import os
from collections.abc import Mapping
from enum import StrEnum
from pathlib import Path

from attr import dataclass

_ENV_DATABASE_KEY = "TASKTRAIL_DB"

DEFAULT_DATABASE_PATH = "app.db"


class _DatabaseConfigSource(StrEnum):
    CLI = "cli"
    ENVIRONMENT = "environment"
    DEFAULT = "default"


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    path: Path
    raw_path: str
    source: _DatabaseConfigSource


def resolve_database_path(
    *,
    cli_value: str | None,
    environ: Mapping[str, str] | None = None,
):
    env = os.environ if environ is None else environ

    if cli_value is not None:
        raw_path = cli_value
        source = _DatabaseConfigSource.CLI
    elif _ENV_DATABASE_KEY in env:
        raw_path = env[_ENV_DATABASE_KEY]
        source = _DatabaseConfigSource.ENVIRONMENT
    else:
        raw_path = DEFAULT_DATABASE_PATH
        source = _DatabaseConfigSource.DEFAULT

    return DatabaseConfig(
        path=Path(raw_path).expanduser().resolve(),
        raw_path=raw_path,
        source=source,
    )
