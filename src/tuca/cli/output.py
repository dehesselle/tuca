# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import json

from tuca.endpoints.endpoint import Endpoint
from tuca.resources.resource import Resource

be_verbose: bool = False


def _to_str(endpoint: Endpoint, resources: dict) -> str:
    if be_verbose:
        resources["header"] = {  # pyright: ignore[reportArgumentType]
            "status_code": endpoint.client.response.status_code,
        }
        resources["header"].update(endpoint.client.response_header.model_dump())

    return json.dumps(
        resources,
        indent=4,
        sort_keys=True,
    )


def to_str[T: Resource](endpoint: Endpoint[T], resources: list[T] | None = None) -> str:
    resources_dict = {
        endpoint.resource_name: [
            resource.to_dict(be_verbose)
            for resource in (resources or endpoint.resources)
        ]
    }
    return _to_str(endpoint, resources_dict)
