from .component import Component, Components


class Firewall(Component):
    pass


class Firewalls(Components):
    def __init__(self):
        super().__init__(Firewall, "firewalls")
        self.response_key = "values"
