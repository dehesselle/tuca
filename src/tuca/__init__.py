# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from tuca.clouding import setup_auth_cli
from tuca.config import config
from tuca.endpoints import (
    setup_actions_endpoint,
    setup_firewalls_endpoint,
    setup_images_endpoint,
    setup_keypairs_endpoint,
    setup_servers_endpoint,
    setup_sizes_endpoint,
    setup_snapshots_endpoint,
)
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
    endpoints = parser.add_subparsers(dest="endpoint", help="manageable resources")
    setup_actions_endpoint(endpoints)
    setup_auth_cli(endpoints)
    setup_firewalls_endpoint(endpoints)
    setup_images_endpoint(endpoints)
    setup_keypairs_endpoint(endpoints)
    setup_servers_endpoint(endpoints)
    setup_snapshots_endpoint(endpoints)
    setup_sizes_endpoint(endpoints)

    args = parser.parse_args()
    config.be_verbose = args.verbose
    try:
        args.func(args)
    except AttributeError:
        parser.print_usage()
