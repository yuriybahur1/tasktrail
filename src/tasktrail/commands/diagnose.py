import argparse

from tasktrail.commands._types import Subparsers


def _handler(args: argparse.Namespace):
    print("Hello")


def register(subparsers: Subparsers) -> None:
    parser = subparsers.add_parser("diagnose")

    parser.set_defaults(handler=_handler)
