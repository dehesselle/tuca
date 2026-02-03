import argparse

from cio.auth import setup_auth_cli
from cio.config import config
from cio.endpoints import (
    setup_keypairs_endpoint,
    setup_servers_endpoint,
    setup_sizes_endpoint,
    setup_snapshots_endpoint,
)
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
    setup_keypairs_endpoint(components)
    setup_servers_endpoint(components)
    setup_snapshots_endpoint(components)
    setup_sizes_endpoint(components)

    args = parser.parse_args()
    config.be_verbose = args.verbose
    try:
        args.func(args)
    except AttributeError:
        parser.print_usage()
