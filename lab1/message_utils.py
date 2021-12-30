import numpy as np
import enum


class Protocol(enum.Enum):
    GBN = enum.auto()
    SRP = enum.auto()


class MessageStatus(enum.Enum):
    OK = enum.auto()
    LOST = enum.auto()


class WindowMessageStatus(enum.Enum):
    BUSY = enum.auto()
    NEED_REPEAT = enum.auto()
    CAN_BE_USED = enum.auto()


class WindowNode:
    def __init__(self, number):
        self.status = WindowMessageStatus.NEED_REPEAT
        self.time = 0
        self.number = number
        pass

    def __str__(self):
        return f"( {self.number}, {self.status}, {self.time})"


class Message:
    number = -1
    real_number = -1
    status = MessageStatus.OK
    data = ""

    def __init__(self):
        pass

    def copy(self):
        msg = Message()
        msg.number = self.number
        msg.status = self.status
        msg.data = self.data

    def __str__(self):
        return f"({self.real_number}({self.number}), {self.status}, {self.data})"


class MsgQueue:

    def __init__(self, loss_probability):
        self.msg_queue = []
        self.loss_probability = loss_probability
        pass

    def is_empty(self):
        return len(self.msg_queue) == 0

    def get_next_message(self):
        if not self.is_empty():
            result = self.msg_queue[0]
            self.msg_queue.pop(0)
            return result
        return None

    def send_message(self, msg):
        self.msg_queue.append(self.distort(msg))

    def distort(self, msg):
        if np.random.rand() <= self.loss_probability:
            msg.status = MessageStatus.LOST

        return msg
