class Topology:
    def __init__(self):
        self.topology = []

    def get_shortest_paths(self, start):
        unvisited = {node: None for node in range(len(self.topology))}

        for i in range(len(self.topology)):
            if len(self.topology[i]) == 0:
                unvisited.pop(i)

        paths = [[] for i in range(len(self.topology))]
        visited = {}
        curr_node = start
        curr_distance = 0

        unvisited[curr_node] = curr_distance
        paths[curr_node].append(start)

        while True:
            for neighbour in self.topology[curr_node]:
                distance = 1
                if neighbour not in unvisited:
                    continue
                new_distance = curr_distance + distance
                if unvisited[neighbour] is None or unvisited[neighbour] > new_distance:
                    unvisited[neighbour] = new_distance
                    paths[neighbour] = paths[curr_node].copy()
                    paths[neighbour].append(neighbour)
            visited[curr_node] = curr_distance
            del unvisited[curr_node]
            if not unvisited:
                break

            candidates = [node for node in unvisited.items() if node[1]]
            if len(candidates) == 0:
                break
            curr_node, curr_distance = sorted(candidates, key=lambda x: x[1])[0]

        return paths

    def add_node(self, new_index):
        count = new_index - len(self.topology) + 1
        for i in range(0, count):
            self.topology.append(set())

    def delete_node(self, index):
        self.topology[index].clear()
        for i in range(len(self.topology)):
            self.topology[i].discard(index)

    def link(self, i, j):
        self.add_node(i)
        self.add_node(j)

        self.topology[i].add(j)
        # self.topology[j].add(i)

    def unlink(self, i, j):
        self.topology[i].discard(j)
        self.topology[j].discard(i)

    def copy(self):
        topology_copy = Topology()
        topology_copy.topology = self.topology.copy()
        return topology_copy

