import argparse
from enum import StrEnum
from cio.version import VERSION
from getpass import getpass
import keyring


class Command(StrEnum):
    AUTH = "auth"


def main() -> None:
    parser = argparse.ArgumentParser(description="unofficial CLI for Clouding.io")
    parser.add_argument("--version", action="version", version=f"cio {VERSION}")
    sp_command = parser.add_subparsers(help="available commands", dest="command")

    _ = sp_command.add_parser(Command.AUTH, help="set API token")

    args = parser.parse_args()

    match args.command:
        case Command.AUTH:
            token = getpass("API token:")
            keyring.set_password("Clouding.io API token", "cio", token)
        case _:
            parser.print_usage()
