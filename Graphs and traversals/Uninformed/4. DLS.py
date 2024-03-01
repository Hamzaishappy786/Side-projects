class Graph:
    def __init__(self):
        self.graph = {}

    def add_nodes(self, node):
        if node not in self.graph:
            self.graph[node] = []

    def add_edges(self, from_, to_, cost=0):
        if from_ not in self.graph:
            self.graph[from_] = []
        if to_ not in self.graph:
            self.graph[to_] = []
        self.graph[from_].append(to_)

    def print(self):
        print(self.graph)

    def DLS(self, start_node, limit=0):
        stack = [(start_node, 0)]
        visited = set()

        while stack:
            node, depth = stack.pop()

            if node not in visited:
                print(node)
                visited.add(node)

                if depth < limit:
                    for node in reversed(self.graph[node]):
                        stack.append((node, depth + 1))

graph = Graph()
graph.add_edges('A', 'B')
graph.add_edges('A', 'C')
graph.add_edges('B', 'C')
graph.add_edges('C', 'D')
graph.DLS('A', 1)
graph.print()
