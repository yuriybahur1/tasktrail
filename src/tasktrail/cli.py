import argparse
from collections.abc import Sequence

from tasktrail.config import resolve_database_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tasktrail",
    )

    parser.add_argument(
        "--db",
        metavar="PATH",
    )

    return parser


def main(argv: Sequence[str] | None = None):
    args = _build_parser().parse_args(argv)

    args.config = resolve_database_path(cli_value=args.db)
