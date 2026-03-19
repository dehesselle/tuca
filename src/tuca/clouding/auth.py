# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import os
from argparse import _SubParsersAction
from enum import StrEnum, auto
from getpass import getpass

import keyring
from keyring.errors import NoKeyringError

SERVICENAME = "CLOUDINGIO_API_TOKEN"
USERNAME = "tuca"

log = logging.getLogger("auth")


class Command(StrEnum):
    CREATE = auto()
    DELETE = auto()


def set_token(_) -> None:
    token = getpass("API token:")
    try:
        keyring.set_password(SERVICENAME, USERNAME, token)
    except NoKeyringError:
        log.error("no keyring available")
        exit(1)


def get_token(_) -> str:
    if api_token := os.getenv(SERVICENAME):
        log.debug("auth via environment variable")
        return api_token
    else:
        try:
            if api_token := keyring.get_password(SERVICENAME, USERNAME):
                log.debug("auth via keyring")
                return api_token
            else:
                log.error("no authentication available")
                exit(1)
        except NoKeyringError:
            log.error("no authentication available")
            exit(1)


def delete_token(_) -> None:
    keyring.delete_password(SERVICENAME, USERNAME)


def setup_auth_cli(subparser: _SubParsersAction):
    auth = subparser.add_parser("auth", help="authentication")
    auth_actions = auth.add_subparsers()
    auth_action_set = auth_actions.add_parser(Command.CREATE, help="set API token")
    auth_action_set.set_defaults(func=set_token)
    auth_action_delete = auth_actions.add_parser(
        Command.DELETE, help="delete API token"
    )
    auth_action_delete.set_defaults(func=delete_token)
