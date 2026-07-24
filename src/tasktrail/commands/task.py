import argparse

from tasktrail.commands._types import Subparsers


def _handler(args: argparse.Namespace):
    match args.task_command:
        case "test":
            pass
        case _:
            pass


def register(subparsers: Subparsers) -> None:
    parser = subparsers.add_parser("task")

    commands = parser.add_subparsers(
        dest="task_command",
        required=True,
    )

    parser.set_defaults(handler=_handler)
