import argparse

from tasktrail.commands._types import Subparsers
from tasktrail.services import initialize


def _handler(args: argparse.Namespace):
    version, applied = initialize(args.config.path)


def register(subparsers: Subparsers) -> None:
    parser = subparsers.add_parser("init")

    parser.set_defaults(handler=_handler)
