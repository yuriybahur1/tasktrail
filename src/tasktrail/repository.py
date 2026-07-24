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


def list_projects(
    conn: sqlite3.Connection,
    include_archived: bool = False,
) -> list[Project]:
    sql = """
        SELECT id, name, description, status, created_at
        FROM projects
    """

    params: tuple[object, ...]

    if not include_archived:
        sql += " WHERE status = ?"
        params = ("active",)

    sql += " ORDER BY name COLLATE NOCASE, id"

    return [_project(row) for row in conn.execute(sql, params)]
