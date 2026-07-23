from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from tasktrail.errors import MigrationError, SchemaCompatibilityError


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    apply: Callable[[sqlite3.Connection], None]


def _v1(conn: sqlite3.Connection) -> None:
    statements = [
        """
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'archived')),
            created_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL
                REFERENCES projects(id)
                ON DELETE RESTRICT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'todo'
                CHECK (
                    status IN (
                        'todo',
                        'in_progress',
                        'done',
                        'archived'
                    )
                ),
            priority TEXT NOT NULL DEFAULT 'medium'
                CHECK (priority IN ('low', 'medium', 'high')),
            due_date TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,

            UNIQUE (project_id, title),

            CHECK (
                (
                    status = 'done'
                    AND completed_at IS NOT NULL
                )
                OR
                (
                    status <> 'done'
                    AND completed_at IS NULL
                )
            )
        )
        """,
        """
        CREATE INDEX idx_tasks_project_status
        ON tasks(project_id, status)
        """,
        """
        CREATE INDEX idx_tasks_due_open
        ON tasks(due_date)
        WHERE
            status IN ('todo', 'in_progress')
            AND due_date IS NOT NULL
        """,
    ]

    for sql in statements:
        conn.execute(sql)


def _v2(conn: sqlite3.Connection) -> None:
    statements = [
        """
        CREATE TABLE tags (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            color TEXT NOT NULL
                CHECK (
                    color GLOB
                    '#[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]'
                    '[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]'
                )
        )
        """,
        """
        CREATE TABLE task_tags (
            task_id INTEGER NOT NULL
                REFERENCES tasks(id)
                ON DELETE CASCADE,
            tag_id INTEGER NOT NULL
                REFERENCES tags(id)
                ON DELETE CASCADE,
            added_at TEXT NOT NULL,

            PRIMARY KEY (task_id, tag_id)
        )
        """,
        """
        CREATE TABLE work_logs (
            id INTEGER PRIMARY KEY,
            task_id INTEGER NOT NULL
                REFERENCES tasks(id)
                ON DELETE RESTRICT,
            minutes INTEGER NOT NULL
                CHECK (minutes BETWEEN 1 AND 1440),
            note TEXT,
            logged_at TEXT NOT NULL
        )
        """,
        """
        CREATE INDEX idx_work_logs_task
        ON work_logs(task_id, logged_at)
        """,
    ]

    for sql in statements:
        conn.execute(sql)


def _v3(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE activity_log (
            id INTEGER PRIMARY KEY,
            task_id INTEGER NOT NULL
                REFERENCES tasks(id)
                ON DELETE CASCADE,
            event_type TEXT NOT NULL
                CHECK (
                    event_type IN (
                        'created',
                        'edited',
                        'completed',
                        'archived'
                    )
                ),
            details TEXT,
            occurred_at TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE INDEX idx_activity_task
        ON activity_log(task_id, occurred_at)
        """
    )

    conn.execute(
        """
        CREATE VIEW project_summary AS
        SELECT
            p.id,
            p.name,
            p.status,
            COUNT(DISTINCT t.id) AS task_count,
            COUNT(
                DISTINCT CASE
                    WHEN t.status = 'done' THEN t.id
                END
            ) AS done_count,
            COALESCE(SUM(w.minutes), 0) AS total_minutes
        FROM projects AS p
        LEFT JOIN tasks AS t
            ON t.project_id = p.id
            AND t.status <> 'archived'
        LEFT JOIN work_logs AS w
            ON w.task_id = t.id
        GROUP BY
            p.id,
            p.name,
            p.status
        """
    )


MIGRATIONS = (
    Migration(
        version=1,
        name="projects and tasks",
        apply=_v1,
    ),
    Migration(
        version=2,
        name="tags and work logs",
        apply=_v2,
    ),
    Migration(
        version=3,
        name="activity and report view",
        apply=_v3,
    ),
)

LATEST_VERSION = MIGRATIONS[-1].version


def ensure_migration_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )


def applied_versions(conn: sqlite3.Connection) -> list[int]:
    table = conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE
            type = 'table'
            AND name = 'schema_migrations'
        """
    ).fetchone()

    if table is None:
        return []

    rows = conn.execute(
        """
        SELECT version
        FROM schema_migrations
        ORDER BY version
        """
    )

    return [int(row[0]) for row in rows]


def validate_history(
    versions: list[int],
    migrations: Sequence[Migration] = MIGRATIONS,
) -> None:
    known_versions = [migration.version for migration in migrations]
    expected_versions = list(range(1, len(known_versions) + 1))

    if known_versions != expected_versions:
        raise MigrationError(
            "application migrations must have contiguous versions starting at 1"
        )

    if versions != known_versions[: len(versions)]:
        raise SchemaCompatibilityError(
            "schema migration history is unknown or inconsistent"
        )


def current_version(conn: sqlite3.Connection) -> int | None:
    versions = applied_versions(conn)
    validate_history(versions)

    return versions[-1] if versions else None


def run_migrations(
    conn: sqlite3.Connection,
    now: str,
    migrations: Sequence[Migration] = MIGRATIONS,
) -> list[Migration]:
    try:
        ensure_migration_table(conn)
        existing_versions = applied_versions(conn)
    except sqlite3.Error as exc:
        raise MigrationError("could not read schema migration history") from exc

    validate_history(existing_versions, migrations)

    applied_migrations: list[Migration] = []

    for migration in migrations[len(existing_versions) :]:
        try:
            conn.execute("BEGIN IMMEDIATE")

            migration.apply(conn)

            conn.execute(
                """
                INSERT INTO schema_migrations (
                    version,
                    name,
                    applied_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    migration.version,
                    migration.name,
                    now,
                ),
            )

            conn.execute("COMMIT")
            applied_migrations.append(migration)

        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")

            raise MigrationError(f"migration {migration.version} failed") from exc

    return applied_migrations
