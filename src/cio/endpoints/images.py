from argparse import _SubParsersAction
from enum import StrEnum, auto

from pydantic import BaseModel

from cio.resource import Resource

from .endpoint import Endpoint


class Action(StrEnum):
    LIST = auto()


class AccessMethods(BaseModel):
    sshKey: str
    password: str


class Image(Resource):
    id: str
    name: str
    accessMethods: AccessMethods
    minimumSizeGb: int | None = None  # 'None' default for reusability in Snapshot


class Images(Endpoint[Image]):
    def __init__(self):
        super().__init__(Image, "images")


def list_images(args):
    images = Images()
    print(images.to_str())


def setup_images_endpoint(subparser: _SubParsersAction):
    images = subparser.add_parser("images", help="manage images")
    images_actions = images.add_subparsers(help="available actions")
    images_action_list = images_actions.add_parser(Action.LIST, help="list snapshots")
    images_action_list.set_defaults(func=list_images)
