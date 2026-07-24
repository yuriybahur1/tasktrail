import sqlite3


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
