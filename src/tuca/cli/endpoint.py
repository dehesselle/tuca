# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from tuca.endpoints.endpoint import Endpoint


def list_resources(endpoint: Endpoint, args: argparse.Namespace):
    if hasattr(args, "id") and args.id:
        if endpoint.get_one(args.id):
            print(endpoint.to_str())
        else:
            print(endpoint.to_str())
    elif hasattr(args, "name") and args.name:
        resource = endpoint.get_one_by_name(args.name)
        print(endpoint.to_str([resource] if resource else []))
    elif hasattr(args, "filter") and args.filter:
        print(endpoint.to_str(endpoint.find(args.filter)))
    else:
        endpoint.get()
        print(endpoint.to_str())
