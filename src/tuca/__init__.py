# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from tuca.clouding import setup_auth_cli
from tuca.cost import setup_cost_cli
from tuca.endpoints import (
    setup_actions_cli,
    setup_firewalls_cli,
    setup_flavors_cli,
    setup_images_cli,
    setup_keypairs_cli,
    setup_servers_cli,
    setup_snapshots_cli,
    setup_volumes_cli,
)
from tuca.endpoints.endpoint import Endpoint
from tuca.log import setup_logging
from tuca.version import VERSION


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(description="(unofficial) CLI for Clouding.io")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="make output verbose",
    )
    parser.add_argument("--version", action="version", version=f"tuca {VERSION}")
    subparsers = parser.add_subparsers(dest="endpoint", help="accessible endpoints")
    setup_actions_cli(subparsers)
    setup_auth_cli(subparsers)  # not an endpoint
    setup_cost_cli(subparsers)  # not an endpoint
    setup_firewalls_cli(subparsers)
    setup_flavors_cli(subparsers)
    setup_images_cli(subparsers)
    setup_keypairs_cli(subparsers)
    setup_servers_cli(subparsers)
    setup_snapshots_cli(subparsers)
    setup_volumes_cli(subparsers)
    args = parser.parse_args()

    Endpoint.be_verbose = args.verbose
    try:
        args.func(args)
    except AttributeError:
        parser.print_usage()
