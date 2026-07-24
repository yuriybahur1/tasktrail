import platform
import sqlite3
from pathlib import Path

from tasktrail.config import DatabaseConfig
from tasktrail.db import BUSY_TIMEOUT_MS, open_read_only
from tasktrail.migrations import LATEST_VERSION, current_version


def diagnose(config: DatabaseConfig) -> list[str]:
    path: Path = config.path

    lines = [
        f"database_path={path}",
        f"config_source={config.source.value}",
        f"parent_exists={str(path.parent.exists()).lower()}",
        f"database_exists={str(path.is_file()).lower()}",
        f"application_schema_version={LATEST_VERSION}",
        f"sqlite_version={sqlite3.sqlite_version}",
        f"python_version={platform.python_version()}",
        f"configured_busy_timeout_ms={BUSY_TIMEOUT_MS}",
    ]

    if not path.is_file():
        lines.extend(
            (
                "schema_version=not_initialized",
                "schema_compatible=false",
                "diagnostic_connection=not_opened",
            )
        )

        return lines

    try:
        with open_read_only(path) as conn:
            foreign_keys = conn.execute("PRAGMA foreign_keys").fetchone()[0]

            journal = conn.execute("PRAGMA journal_mode").fetchone()[0]

            synchronous = conn.execute("PRAGMA synchronous").fetchone()[0]

            busy = conn.execute("PRAGMA busy_timeout").fetchone()[0]

            try:
                version: int | None | str = current_version(conn)
            except Exception:
                version = "unreadable"

        lines.extend(
            (
                f"schema_version={version if version is not None else 'not_initialized'}",
                f"schema_compatible={str(version == LATEST_VERSION).lower()}",
                f"diagnostic_foreign_keys={foreign_keys}",
                f"journal_mode={journal}",
                f"diagnostic_synchronous={synchronous}",
                f"diagnostic_busy_timeout_ms={busy}",
            )
        )
    except Exception as exc:
        lines.extend(
            (
                "schema_version=unreadable",
                "schema_compatible=false",
                f"diagnostic_error={type(exc).__name__}",
            )
        )

    return lines
