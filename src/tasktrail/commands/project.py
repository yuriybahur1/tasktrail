import argparse

from tasktrail import formatting, services
from tasktrail.commands._types import Subparsers


def _handler(args: argparse.Namespace):
    match args.project_command:
        case "add":
            print(
                f"created project id={services.add_project(path=args.config.path, name=args.name, description=args.description)}"
            )
        case "list":
            for x in services.list_projects(args.config.path, args.include_archived):
                print(formatting.project_line(x))
        case "archive":
            services.archive_project(args.config.path, args.project_id)
            # _out(f"archived project id={a.project_id}")
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

    archive_parser = commands.add_parser("archive")
    archive_parser.add_argument("project_id", type=int)

    parser.set_defaults(handler=_handler)
