from collections.abc import Callable
from pathlib import Path

from tasktrail.db import open_database
from tasktrail.timeutils import utc_now_iso


def initialize_database(
    path: Path, *, clock: Callable[[], str] = utc_now_iso
) -> tuple[int, tuple[str, ...]]:
    with open_database(path, create=True) as conn:
        pass

    return 1, ("", "")
