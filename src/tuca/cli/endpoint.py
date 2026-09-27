# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from tuca.cli.output import to_str
from tuca.endpoints.endpoint import Endpoint


def list_resources(endpoint: Endpoint, args: argparse.Namespace):
    if hasattr(args, "id") and args.id:
        if endpoint.get_one(args.id):
            print(to_str(endpoint))
        else:
            print(to_str(endpoint))
    elif hasattr(args, "name") and args.name:
        resource = endpoint.get_one_by_name(args.name)
        print(to_str(endpoint, [resource] if resource else []))
    elif hasattr(args, "filter") and args.filter:
        print(to_str(endpoint, endpoint.find(args.filter)))
    else:
        endpoint.get()
        print(to_str(endpoint))
