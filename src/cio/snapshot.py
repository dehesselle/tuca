from cio.component import Component, Components


class Snapshot(Component):
    pass


class Snapshots(Components):
    def __init__(self):
        super().__init__(Snapshot, "snapshots")
