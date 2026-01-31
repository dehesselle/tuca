import argparse
from enum import StrEnum
from cio.version import VERSION


class Command(StrEnum):
    AUTH = "auth"


def main() -> None:
    parser = argparse.ArgumentParser(description="unofficial CLI for Clouding.io")
    parser.add_argument("--version", action="version", version=f"cio {VERSION}")
    sp_command = parser.add_subparsers(help="available commands", dest="command")

    p_auth = sp_command.add_parser(Command.AUTH, help="set API token")
    p_auth.add_argument("token", type=str, help="API token")

    args = parser.parse_args()

    match args.command:
        case Command.AUTH:
            pass
        case _:
            parser.print_usage()
