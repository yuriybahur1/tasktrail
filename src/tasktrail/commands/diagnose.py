import argparse

from tasktrail.commands._types import Subparsers
from tasktrail.diagnostics import diagnose


def _handler(args: argparse.Namespace):
    for line in diagnose(args.config):
        print(line)


def register(subparsers: Subparsers) -> None:
    parser = subparsers.add_parser("diagnose")

    parser.set_defaults(handler=_handler)
