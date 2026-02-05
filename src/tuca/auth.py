# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import os
from argparse import _SubParsersAction
from enum import StrEnum, auto
from getpass import getpass

import keyring

SERVICENAME = "Clouding.io API token"
USERNAME = "tuca"


class Action(StrEnum):
    CREATE = auto()
    DELETE = auto()


def set_token(_) -> None:
    token = getpass("API token:")
    keyring.set_password(SERVICENAME, USERNAME, token)


def get_token(_) -> str:
    if api_token := os.getenv("CLOUDINGIO_API_TOKEN"):
        return api_token
    else:
        return keyring.get_password(SERVICENAME, USERNAME)


def delete_token(_) -> None:
    keyring.delete_password(SERVICENAME, USERNAME)


def setup_auth_cli(subparser: _SubParsersAction):
    auth = subparser.add_parser("auth", help="manage authentication token")
    auth_actions = auth.add_subparsers()
    auth_action_set = auth_actions.add_parser(
        Action.CREATE, help="set authentication token"
    )
    auth_action_set.set_defaults(func=set_token)
    auth_action_delete = auth_actions.add_parser(
        Action.DELETE, help="delete authentication token"
    )
    auth_action_delete.set_defaults(func=delete_token)
