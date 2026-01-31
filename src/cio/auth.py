from getpass import getpass

import keyring

SERVICENAME = "Clouding.io API token"
USERNAME = "cio"


def set_token(_) -> None:
    token = getpass("API token:")
    keyring.set_password(SERVICENAME, USERNAME, token)


def get_token(_) -> str:
    return keyring.get_password(SERVICENAME, USERNAME)


def delete_token(_) -> None:
    keyring.delete_password(SERVICENAME, USERNAME)


# reason to turn this into a class: create a response in JSON like all others
