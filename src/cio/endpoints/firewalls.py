from cio.resource import Resource

from .endpoint import Endpoint


class Firewall(Resource):
    id: str
    name: str


class Firewalls(Endpoint[Firewall]):
    def __init__(self):
        super().__init__(Firewall, "firewalls")
        self.response_key = "values"
