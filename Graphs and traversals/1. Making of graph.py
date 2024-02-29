class Graph:
    def __init__(self):
        self.graph = {}

    def add_nodes(self, node):
        if node not in self.graph:
            self.graph[node] = []

    def add_edges(self, from_, to_, cost=1):
        self.graph[from_].append(to_)
        self.graph[from_].append(cost)

    def print(self):
        print(self.graph)


graph = Graph()
graph.add_nodes('A')
graph.add_nodes('B')
graph.add_edges('A', 'B', 20)
graph.print()
