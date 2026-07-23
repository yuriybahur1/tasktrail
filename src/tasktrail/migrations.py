import sqlite3
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Migration:
    version: int
    name: str
    apply: Callable[[sqlite3.Connection], None]


def _ensure_migration_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL
        ) STRICT
        """
    )


def _applied_versions(conn: sqlite3.Connection) -> list[int]:
    table = conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = 'schema_migrations'
        """
    ).fetchone()

    if table is None:
        return []

    return [
        int(row[0])
        for row in conn.execute(
            """
            SELECT version
            FROM schema_migrations
            ORDER BY version
            """
        )
    ]


def run_migrations(conn: sqlite3.Connection):
    try:
        _ensure_migration_table(conn)

        existing = _applied_versions(conn)
    except sqlite3.Error:
        pass
