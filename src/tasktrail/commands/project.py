import argparse

from tasktrail import services
from tasktrail.commands._types import Subparsers


def _handler(args: argparse.Namespace):
    match args.project_command:
        case "add":
            print(
                f"created project id={services.add_project(path=args.config.path, name=args.name, description=args.description)}"
            )
        case "list":
            for x in services.list_projects(args.config.path, args.include_archived):
                pass
        case _:
            pass


def register(subparsers: Subparsers) -> None:
    parser = subparsers.add_parser("project")

    commands = parser.add_subparsers(
        dest="project_command",
        required=True,
    )

    add_parser = commands.add_parser("add")
    add_parser.add_argument("name")
    add_parser.add_argument("--description")

    list_parser = commands.add_parser("list")
    list_parser.add_argument("--include-archived", action="store_true")

    parser.set_defaults(handler=_handler)
