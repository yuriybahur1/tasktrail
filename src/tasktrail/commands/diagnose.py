import argparse

from tasktrail.commands._types import Subparsers
from tasktrail.db import open_read_only


def _handler(args: argparse.Namespace):
    with open_read_only(args.config.path) as conn:
        pass


def register(subparsers: Subparsers) -> None:
    parser = subparsers.add_parser("diagnose")

    parser.set_defaults(handler=_handler)
