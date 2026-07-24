import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from tasktrail.errors import DatabaseError, DatabaseNotInitializedError

BUSY_TIMEOUT_MS = 5000

_SYNCHRONOUS = "NORMAL"

_CONNECT_TIMEOUT_SECONDS = 5.0


def _configure_connection(connection: sqlite3.Connection, *, writable: bool) -> None:
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    if writable:
        mode = connection.execute("PRAGMA journal_mode = WAL").fetchone()

        if mode is None or str(mode[0]).lower() != "wal":
            raise DatabaseError("SQLite could not enable WAL journal mode")

        connection.execute(f"PRAGMA synchronous = {_SYNCHRONOUS}")

    connection.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")


@contextmanager
def open_database(path: Path, *, create: bool = False) -> Generator[sqlite3.Connection]:
    if not path.exists() and not create:
        raise DatabaseNotInitializedError(
            "database not initialized; run 'tasktrail init'"
        )

    if create:
        path.parent.mkdir(parents=True, exist_ok=True)

    connection: sqlite3.Connection | None = None

    try:
        connection = sqlite3.connect(
            path,
            timeout=_CONNECT_TIMEOUT_SECONDS,
            isolation_level=None,
        )

        _configure_connection(connection, writable=True)
    except DatabaseError:
        if connection is not None:
            connection.close()
        raise
    except sqlite3.Error as exc:
        if connection is not None:
            connection.close()
        raise DatabaseError("database operation failed") from exc

    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def open_read_only(path: Path) -> Generator[sqlite3.Connection]:
    if not path.exists():
        raise DatabaseNotInitializedError("database is not initialized")

    connection: sqlite3.Connection | None = None

    try:
        uri = f"{path.resolve().as_uri()}?mode=ro"

        connection = sqlite3.connect(
            uri,
            uri=True,
            timeout=_CONNECT_TIMEOUT_SECONDS,
            isolation_level=None,
        )

        connection.row_factory = sqlite3.Row

        connection.execute("PRAGMA foreign_keys = ON")

        connection.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
    except sqlite3.Error as exc:
        if connection is not None:
            connection.close()
        raise DatabaseError("database diagnostic failed") from exc

    try:
        yield connection
    finally:
        connection.close()
