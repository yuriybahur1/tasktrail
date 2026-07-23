import argparse

from tasktrail.commands._types import Subparsers
from tasktrail.services import initialize_database


def _handler(args: argparse.Namespace):
    initialize_database(args.config.path)


def register(subparsers: Subparsers) -> None:
    parser = subparsers.add_parser("init")

    parser.set_defaults(handler=_handler)
