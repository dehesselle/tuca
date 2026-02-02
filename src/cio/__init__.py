import argparse

from cio.auth import setup_auth_cli
from cio.components import setup_keypairs_cli, setup_servers_cli, setup_snapshots_cli
from cio.config import config
from cio.version import VERSION


def main() -> None:
    parser = argparse.ArgumentParser(description="unofficial CLI for Clouding.io")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="make output verbose",
    )
    parser.add_argument("--version", action="version", version=f"cio {VERSION}")
    components = parser.add_subparsers(help="manageable components", dest="component")
    setup_auth_cli(components)
    setup_keypairs_cli(components)
    setup_servers_cli(components)
    setup_snapshots_cli(components)

    args = parser.parse_args()
    config.be_verbose = args.verbose
    try:
        args.func(args)
    except AttributeError:
        parser.print_usage()
