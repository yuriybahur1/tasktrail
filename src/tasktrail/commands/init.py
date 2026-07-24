import argparse

from tasktrail.commands._types import Subparsers
from tasktrail.services import initialize


def _handler(args: argparse.Namespace):
    version, applied = initialize(args.config.path)

    print(f"database={args.config.path}")

    print(f"schema_version={version}")

    print(f"applied_migrations={len(applied)}")

    for item in applied:
        print(f"applied={item}")


def register(subparsers: Subparsers) -> None:
    parser = subparsers.add_parser("init")

    parser.set_defaults(handler=_handler)
