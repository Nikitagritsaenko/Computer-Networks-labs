import time
from threading import Thread

import numpy as np

from lab2 import topology as topology_module
from lab2.message import Message, MessageType


class Connection:
    def __init__(self):
        self.out_queue = []
        self.in_queue = []

    def __str__(self):
        return f"(->:{self.out_queue}\n<-:{self.in_queue})"

    @staticmethod
    def __get_message(queue):
        if len(queue) > 0:
            return queue.pop(0)
        else:
            return None

    def get_message(self, direction=0):
        if direction == 0:
            return self.__get_message(self.out_queue)
        else:
            return self.__get_message(self.in_queue)

    def send_message(self, message, direction=0):
        if direction == 0:
            self.in_queue.append(message)
        else:
            self.out_queue.append(message)


class Router:

    def __init__(self, conn, index):
        self.DR_connection = conn
        self.topology = topology_module.Topology()
        self.index = index
        self.shortest_paths = []
        self.neighbours = []

    def print_shortest_paths(self):
        shortest_paths = self.topology.get_shortest_paths(self.index)
        print(f"{self.index}: {shortest_paths}\n", end="")

    def send_neighbours(self):
        message = Message()
        message.type = MessageType.SEND_NEIGHBOURS
        message.data = self.neighbours.copy()
        self.DR_connection.send_message(message)

    def get_topology(self):
        message = Message()
        message.type = MessageType.GET_TOPOLOGY
        self.DR_connection.send_message(message)

    def start(self):
        self.send_neighbours()
        self.get_topology()

    def off(self):
        message = Message()
        message.type = MessageType.REMOVE_NODE
        self.DR_connection.send_message(message)

    def add_node(self, index, neighbours):
        self.topology.add_node(index)
        for j in neighbours:
            self.topology.link(index, j)

        if index in self.neighbours:
            if index not in self.topology.topology[self.index]:
                message = Message()
                message.type = MessageType.SEND_NEIGHBOURS
                message.data = [index]
                self.DR_connection.send_message(message)

    def delete_node(self, index):
        self.topology.delete_node(index)

    def process_message(self):
        input_message = self.DR_connection.get_message()

        if input_message is None:
            return

        print(f"router #{self.index} received : {input_message}\n")

        if input_message.type == MessageType.SEND_NEIGHBOURS:
            self.add_node(input_message.data["index"], input_message.data["neighbours"])
        elif input_message.type == MessageType.UPDATE_TOPOLOGY:
            self.topology = input_message.data
        elif input_message.type == MessageType.REMOVE_NODE:
            self.delete_node(input_message.data)
        elif input_message.type == MessageType.PRINT_SHORTEST_PATHS:
            self.print_shortest_paths()
        else:
            raise Exception(f"Unsupported type of message:{input_message.type}")


class DesignatedRouter:

    def __init__(self):
        self.connections = []
        self.topology = topology_module.Topology()

    def add_connection(self):
        new_connection = Connection()
        new_index = len(self.connections)
        self.connections.append(new_connection)
        return new_connection, new_index

    def add_node(self, index, neighbours):
        self.topology.add_node(index)
        for j in neighbours:
            self.topology.link(index, j)

    def delete_node(self, index):
        self.topology.delete_node(index)

    def send_all_exclude_one(self, exclude_index, message):
        for connection_index in range(len(self.connections)):
            conn = self.connections[connection_index]
            if conn is None:
                continue
            if connection_index == exclude_index:
                continue
            conn.send_message(message, direction=1)

    def process_message_neighbours(self, connection_index, input_message):
        self.add_node(connection_index, input_message.data)

        message = Message()
        message.type = MessageType.SEND_NEIGHBOURS
        message.data = {"index": connection_index, "neighbours": input_message.data}

        self.send_all_exclude_one(connection_index, message)

    def process_message_remove_node(self, connection_index):
        self.delete_node(connection_index)

        message = Message()
        message.type = MessageType.REMOVE_NODE
        message.data = connection_index

        self.send_all_exclude_one(connection_index, message)

    def print_shortest_paths(self):
        message = Message()
        message.type = MessageType.PRINT_SHORTEST_PATHS
        for connection in self.connections:
            connection.send_message(message, direction=1)

    def process_message(self):
        for connection_index in range(len(self.connections)):
            connection = self.connections[connection_index]
            if connection is None:
                continue

            input_message = connection.get_message(direction=1)

            if input_message is None:
                continue

            print(f"Designated router received message from router #{connection_index}: {input_message}\n", end="")

            if input_message.type == MessageType.SEND_NEIGHBOURS:
                self.process_message_neighbours(connection_index, input_message)
            elif input_message.type == MessageType.GET_TOPOLOGY:
                message = Message()
                message.type = MessageType.UPDATE_TOPOLOGY
                message.data = self.topology.copy()
                connection.send_message(message, direction=1)
            elif input_message.type == MessageType.REMOVE_NODE:
                self.process_message_remove_node(connection_index)
            else:
                raise Exception(f"Unsupported type of message:{input_message.type}")


designated_router: DesignatedRouter = None

stop_flag = False
verbose = False
blink_connections_arr = []


def router_run(neighbours):
    global designated_router
    global blink_connections_arr

    conn, index = designated_router.add_connection()
    router = Router(conn, index)
    router.neighbours = neighbours.copy()
    router.start()

    while True:
        router.process_message()
        if blink_connections_arr[router.index]:
            router.off()
            time.sleep(2)
            router.start()
            blink_connections_arr[router.index] = False

        if stop_flag:
            break


def designated_router_run():
    global designated_router
    global verbose
    designated_router = DesignatedRouter()

    while True:
        designated_router.process_message()
        if verbose:
            designated_router.print_shortest_paths()
            verbose = False
        if stop_flag:
            break


def printer():
    global verbose
    while True:
        time.sleep(1)
        verbose = True
        if stop_flag:
            break


def connections_breaker(threshold=0.5):
    global blink_connections_arr
    time.sleep(2)
    while True:
        time.sleep(0.01)
        val = np.random.rand()
        if val >= threshold:
            index = np.random.randint(0, len(blink_connections_arr))
            blink_connections_arr[index] = True
            time.sleep(2)

        if stop_flag:
            break


def simulate(topology):
    global blink_connections_arr
    global stop_flag

    nodes = topology["nodes"]
    neighbours = topology["neighbours"]

    blink_connections_arr = [False for i in range(len(nodes))]

    dr_thread = Thread(target=designated_router_run, args=())

    router_threads = [Thread(target=router_run, args=(neighbours[i],)) for i in range(len(nodes))]

    dr_thread.start()
    for i in range(len(nodes)):
        router_threads[i].start()


    printer_thread = Thread(target=printer, args=())
    conn_breaker_thread = Thread(target=connections_breaker, args=())
    conn_breaker_thread.start()
    printer_thread.start()

    time.sleep(5)
    stop_flag = True
    for i in range(len(nodes)):
        router_threads[i].join()

    dr_thread.join()
