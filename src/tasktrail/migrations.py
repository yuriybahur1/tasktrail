import sqlite3
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class _Migration:
    version: int
    name: str
    apply: Callable[[sqlite3.Connection], None]
