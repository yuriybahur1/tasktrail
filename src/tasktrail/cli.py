import argparse
import os
from collections.abc import Sequence

from tasktrail.config import resolve_database_path

_ENV_DEBUG_KEY = "ENV_DEBUG"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tasktrail",
    )

    parser.add_argument(
        "--db",
        metavar="PATH",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
    )

    return parser


def main(argv: Sequence[str] | None = None):
    args = _build_parser().parse_args(argv)

    args.config = resolve_database_path(cli_value=args.db)

    debug = args.debug or os.environ.get(_ENV_DEBUG_KEY, "") in {"1", "yes", "true"}
