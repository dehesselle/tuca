# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import logging
import sys

from tuca.cli.firewalls import add_command_firewalls
from tuca.cli.flavors import add_command_flavors
from tuca.cli.images import add_command_images
from tuca.cli.snapshots import add_command_snapshots
from tuca.cli.volumes import add_command_volumes
from tuca.clouding import AuthError, add_auth_command
from tuca.cost import add_cost_command
from tuca.endpoints.actions import add_actions_command
from tuca.endpoints.endpoint import Endpoint, EndpointError
from tuca.endpoints.keypairs import add_keypairs_command
from tuca.endpoints.servers import add_servers_command
from tuca.log import setup_logging
from tuca.version import VERSION

log = logging.getLogger("main")


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
    commands = parser.add_subparsers(help="available commands")
    add_actions_command(commands)
    add_auth_command(commands)
    add_cost_command(commands)
    add_command_firewalls(commands)
    add_command_flavors(commands)
    add_command_images(commands)
    add_keypairs_command(commands)
    add_servers_command(commands)
    add_command_snapshots(commands)
    add_command_volumes(commands)

    args = parser.parse_args()
    Endpoint.be_verbose = args.verbose

    try:
        args.func(args)
    except AttributeError:
        parser.print_usage()
        sys.exit(1)
    except (AuthError, EndpointError) as e:
        log.error(e)
        sys.exit(1)
