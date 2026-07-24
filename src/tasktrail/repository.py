import sqlite3

from tasktrail.models import Project


def create_project(
    conn: sqlite3.Connection,
    name: str,
    description: str | None,
    now: str,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO projects(name, description, created_at)
        VALUES (?, ?, ?)
        """,
        (name, description, now),
    )

    if cursor.lastrowid is None:
        raise RuntimeError("SQLite did not return a project id")

    return int(cursor.lastrowid)


def _project(row: sqlite3.Row) -> Project:
    return Project(
        row["id"],
        row["name"],
        row["description"],
        row["status"],
        row["created_at"],
    )


def list_projects(
    conn: sqlite3.Connection,
    include_archived: bool = False,
) -> list[Project]:
    sql = """
        SELECT id, name, description, status, created_at
        FROM projects
    """

    params: tuple[object, ...] = tuple()

    if not include_archived:
        sql += " WHERE status = ?"
        params = ("active",)

    sql += " ORDER BY name COLLATE NOCASE, id"

    return [_project(row) for row in conn.execute(sql, params)]


def get_project(
    conn: sqlite3.Connection,
    project_id: int,
) -> Project | None:
    row = conn.execute(
        """
        SELECT id, name, description, status, created_at
        FROM projects
        WHERE id = ?
        """,
        (project_id,),
    ).fetchone()

    return _project(row) if row else None


def count_open_project_tasks(
    conn: sqlite3.Connection,
    project_id: int,
) -> int:
    row = conn.execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE project_id = ?
          AND status IN ('todo', 'in_progress')
        """,
        (project_id,),
    ).fetchone()

    if row is None:
        raise RuntimeError("SQLite did not return an aggregate row")

    return int(row[0])


def archive_project(
    conn: sqlite3.Connection,
    project_id: int,
) -> int:
    return conn.execute(
        """
        UPDATE projects
        SET status = 'archived'
        WHERE id = ?
          AND status = 'active'
        """,
        (project_id,),
    ).rowcount
