import sqlite3

from tasktrail.errors import DatabaseError

_BUSY_TIMEOUT_MS = 5000

_SYNCHRONOUS = "NORMAL"


def _configure_connection(connection: sqlite3.Connection, *, writable: bool) -> None:
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    if writable:
        mode = connection.execute("PRAGMA journal_mode = WAL").fetchone()

        if mode is None or str(mode[0]).lower() != "wal":
            raise DatabaseError("SQLite could not enable WAL journal mode")

        connection.execute(f"PRAGMA synchronous = {_SYNCHRONOUS}")

    connection.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_MS}")
