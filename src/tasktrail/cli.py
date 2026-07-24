import argparse
import os
import sys
import traceback
from collections.abc import Sequence

from tasktrail.commands import diagnose, init, project
from tasktrail.config import resolve_database_path
from tasktrail.errors import AppError

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

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    init.register(subparsers)

    diagnose.register(subparsers)

    project.register(subparsers)

    return parser


def main(argv: Sequence[str] | None = None):
    args = _build_parser().parse_args(argv)

    args.config = resolve_database_path(cli_value=args.db)

    debug = args.debug or os.environ.get(_ENV_DEBUG_KEY, "") in {"1", "yes", "true"}

    try:
        args.handler(args)

        return 0
    except AppError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        if debug:
            traceback.print_exc(file=sys.stderr)
        else:
            print(f"Internal error: {exc}; rerun with --debug", file=sys.stderr)
        return 70
