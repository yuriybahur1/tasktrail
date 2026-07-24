import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import cast

from tasktrail import repository
from tasktrail.db import open_database
from tasktrail.errors import (
    ConflictError,
    DatabaseNotInitializedError,
    NotFoundError,
    SchemaCompatibilityError,
    ValidationError,
)
from tasktrail.migrations import LATEST_VERSION, current_version, run_migrations
from tasktrail.models import Priority, Project
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

            return repository.create_project(conn, name, description, clock())
    except sqlite3.IntegrityError as exc:
        raise ConflictError("a project with that name already exists") from exc


def list_projects(
    path: Path,
    include_archived: bool = False,
) -> list[Project]:
    with open_database(path) as conn:
        _verify(conn)

        return repository.list_projects(conn, include_archived)


def archive_project(path: Path, project_id: int) -> None:
    with open_database(path) as conn:
        _verify(conn)

        try:
            conn.execute("BEGIN IMMEDIATE")

            project = repository.get_project(conn, project_id)

            if project is None:
                raise NotFoundError(f"project {project_id} was not found")

            if project.status == "archived":
                raise ConflictError("project is already archived")

            if repository.count_open_project_tasks(conn, project_id) != 0:
                raise ConflictError("cannot archive a project with open tasks")

            if repository.archive_project(conn, project_id) != 1:
                raise ConflictError("project state changed while archiving it")
            conn.execute("COMMIT")
        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise


def priority(value: str) -> str:
    try:
        return Priority(value).value
    except ValueError as exc:
        raise ValidationError("priority must be low, medium, or high") from exc


def add_task(
    path: Path,
    project_id: int,
    title: str,
    description: str | None,
    priority_value: str,
    due: str | None,
    clock: Callable[[], str] = utc_now_iso,
) -> int:
    title = required_text(title, "task title")

    description = optional_text(description, "description")

    priority_value = priority(priority_value)
    # due = due_date(due)
    # now = clock()

    # try:
    #     with _checked(path) as conn:
    #         _verify(conn)

    #         try:
    #             conn.execute("BEGIN IMMEDIATE")

    #             project = repository.get_project(conn, project_id)
    #             if project is None:
    #                 raise NotFoundError(f"project {project_id} was not found")

    #             if project.status != "active":
    #                 raise ConflictError(
    #                     "cannot add a task to an archived project"
    #                 )

    #             task_id = repository.create_task(
    #                 conn,
    #                 project_id,
    #                 title,
    #                 description,
    #                 priority_value,
    #                 due,
    #                 now,
    #             )

    #             repository.insert_activity(
    #                 conn,
    #                 task_id,
    #                 "created",
    #                 None,
    #                 now,
    #             )

    #             conn.execute("COMMIT")
    #             return task_id

    #         except Exception:
    #             if conn.in_transaction:
    #                 conn.execute("ROLLBACK")
    #             raise

    # except sqlite3.IntegrityError as exc:
    #     raise ConflictError(
    #         "a task with that title already exists in the project"
    #     ) from exc
