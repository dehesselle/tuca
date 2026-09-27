# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import json

from tuca.client import Client


def print_total_cost_per_hour(client: Client, _) -> None:
    cost = {
        "servers": client.servers.hourly_cost(),
        "snapshots": client.snapshots.hourly_cost(),
    }
    cost["total"] = sum(cost.values())
    print(
        json.dumps(
            {"cost": cost},
            indent=4,
            sort_keys=True,
        )
    )


def add_command_cost(subparser: argparse._SubParsersAction):
    cost = subparser.add_parser("cost", help="hourly costs")
    cost.set_defaults(func=print_total_cost_per_hour)
