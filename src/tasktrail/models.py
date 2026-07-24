from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class Project:
    id: int
    name: str
    description: str | None
    status: str
    created_at: str


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class Task:
    id: int
    project_id: int
    project_name: str
    title: str
    description: str | None
    status: str
    priority: str
    due_date: str | None
    created_at: str
    completed_at: str | None
    tags: str | None
