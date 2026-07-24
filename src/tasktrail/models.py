from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Project:
    id: int
    name: str
    description: str | None
    status: str
    created_at: str
