import argparse

from tasktrail.commands._types import Subparsers


def _handler(args: argparse.Namespace):
    match args.task_command:
        case "add":
            pass
        case _:
            pass


def register(subparsers: Subparsers) -> None:
    parser = subparsers.add_parser("task")

    commands = parser.add_subparsers(
        dest="task_command",
        required=True,
    )

    add_parser = commands.add_parser("add")
    add_parser.add_argument("project_id", type=int)
    add_parser.add_argument("title")
    add_parser.add_argument("--description")
    add_parser.add_argument(
        "--priority",
        default="medium",
        choices=("low", "medium", "high"),
    )
    add_parser.add_argument("--due")

    parser.set_defaults(handler=_handler)
