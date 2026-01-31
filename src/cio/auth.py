from getpass import getpass

import keyring

SERVICENAME = "Clouding.io API token"
USERNAME = "cio"


def set_token() -> None:
    token = getpass("API token:")
    keyring.set_password(SERVICENAME, USERNAME, token)


def get_token() -> str:
    return keyring.get_password(SERVICENAME, USERNAME)


def delete_token() -> None:
    keyring.delete_password(SERVICENAME, USERNAME)
