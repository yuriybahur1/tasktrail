import sqlite3
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class _Migration:
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
        ) STRICT
        """,
        """
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL
                REFERENCES projects(id) ON DELETE RESTRICT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'todo'
                CHECK (status IN ('todo', 'in_progress', 'done', 'archived')),
            priority TEXT NOT NULL DEFAULT 'medium'
                CHECK (priority IN ('low', 'medium', 'high')),
            due_date TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            UNIQUE (project_id, title),
            CHECK (
                (status = 'done' AND completed_at IS NOT NULL)
                OR
                (status <> 'done' AND completed_at IS NULL)
            )
        ) STRICT
        """,
        """
        CREATE INDEX idx_tasks_project_status
            ON tasks (project_id, status)
        """,
        """
        CREATE INDEX idx_tasks_due_open
            ON tasks (due_date)
            WHERE status IN ('todo', 'in_progress')
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
                    '#[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]'
                )
        ) STRICT
        """
        """
        CREATE TABLE task_tags (
            task_id INTEGER NOT NULL
                REFERENCES tasks(id) ON DELETE CASCADE,
            tag_id INTEGER NOT NULL
                REFERENCES tags(id) ON DELETE CASCADE,
            added_at TEXT NOT NULL,
            PRIMARY KEY (task_id, tag_id)
        ) STRICT
        """,
        """
        CREATE TABLE work_logs (
            id INTEGER PRIMARY KEY,
            task_id INTEGER NOT NULL
                REFERENCES tasks(id) ON DELETE RESTRICT,
            minutes INTEGER NOT NULL
                CHECK (minutes BETWEEN 1 AND 1440),
            note TEXT,
            logged_at TEXT NOT NULL
        ) STRICT
        """,
        """
        CREATE INDEX idx_work_logs_task
            ON work_logs (task_id, logged_at);
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
                REFERENCES tasks(id) ON DELETE CASCADE,
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
            ON activity_log (task_id, occurred_at)
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


_MIGRATIONS = (
    _Migration(1, "projects and tasks", _v1),
    _Migration(2, "tags and work logs", _v2),
    _Migration(3, "activity and report view", _v3),
)

_LATEST_VERSION = _MIGRATIONS[-1].version


def _ensure_migration_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )


def _applied_versions(conn: sqlite3.Connection) -> list[int]:
    table = conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'schema_migrations'
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
