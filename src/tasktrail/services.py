import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import cast

from tasktrail.db import open_database
from tasktrail.errors import (
    ConflictError,
    DatabaseNotInitializedError,
    SchemaCompatibilityError,
)
from tasktrail.migrations import LATEST_VERSION, current_version, run_migrations
from tasktrail.repository import create_project
from tasktrail.timeutils import utc_now_iso
from tasktrail.validation import optional_text, required_text


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


def _verify(conn: sqlite3.Connection) -> None:
    version = current_version(conn)

    if version is None:
        raise DatabaseNotInitializedError(
            "database is not initialized; run 'tasktrail init'"
        )

    if version != LATEST_VERSION:
        raise SchemaCompatibilityError(
            f"database schema version {version} is incompatible "
            f"with required version {LATEST_VERSION}"
        )


def add_project(
    *,
    path: Path,
    name: str,
    description: str | None,
    clock: Callable[[], str] = utc_now_iso,
) -> int:
    name = required_text(name, "project name")

    description = optional_text(description, "description")

    try:
        with open_database(path) as conn:
            _verify(conn)

            return create_project(conn, name, description, clock())
    except sqlite3.IntegrityError as exc:
        raise ConflictError("a project with that name already exists") from exc
