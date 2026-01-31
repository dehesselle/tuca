from cio.clouding import Clouding


class Servers(Clouding):
    def __init__(self):
        super().__init__()
        pass

    def list(self):
        self.get("servers")
        self.response["servers"] = self._response.json()["servers"]
        self.print()
