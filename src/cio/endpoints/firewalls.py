from cio.resource import Resource

from .endpoint import Endpoint


class Firewall(Resource):
    pass


class Firewalls(Endpoint[Firewall]):
    def __init__(self):
        super().__init__(Firewall, "firewalls")
        self.response_key = "values"
