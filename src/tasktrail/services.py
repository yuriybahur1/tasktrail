from collections.abc import Callable
from pathlib import Path
from typing import cast

from tasktrail.db import open_database
from tasktrail.errors import SchemaCompatibilityError
from tasktrail.migrations import LATEST_VERSION, current_version, run_migrations
from tasktrail.timeutils import utc_now_iso


def initialize(
    path: Path,
    clock: Callable[[], str] = utc_now_iso,
) -> tuple[int, list[str]]:
    with open_database(path, create=True) as conn:
        applied = run_migrations(conn, now=clock())

        version = current_version(conn)

    if version != LATEST_VERSION:
        raise SchemaCompatibilityError("database schema is not current")

    return cast(int, version), [
        f"{migration.version}: {migration.name}" for migration in applied
    ]
