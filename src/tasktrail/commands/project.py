import argparse

from tasktrail.commands._types import Subparsers


def _handler(args: argparse.Namespace):
    match args.project_command:
        case "add":
            # _out(
            #     f"created project id={services.add_project(_path(a), a.name, a.description)}"
            # )
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

    parser.set_defaults(handler=_handler)
