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
