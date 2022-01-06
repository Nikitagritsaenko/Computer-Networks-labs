import enum


class MessageType(enum.Enum):
    SEND_NEIGHBOURS = enum.auto()
    GET_TOPOLOGY = enum.auto()
    UPDATE_TOPOLOGY = enum.auto()
    REMOVE_NODE = enum.auto()
    PRINT_SHORTEST_PATHS = enum.auto()


class Message:
    def __init__(self):
        self.data = None
        self.type = None

    def __str__(self):
        return f"({self.type}: {self.data})"
