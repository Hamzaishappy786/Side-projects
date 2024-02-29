class Graph:
    def __init__(self):
        self.graph = {}

    def add_nodes(self, node):
        self.graph[node] = []

    def add_edges(self, from_, to_, cost=0):
        if from_ not in self.graph:
            self.add_nodes(from_)
        if to_ not in self.graph:
            self.add_nodes(to_)
        self.graph[from_].append(to_)
        # self.graph[from_].append(cost)     Same is the case in DFS

    def DFS(self, start_node):
        stack = [start_node]
        visited = set()

        while stack:
            node = stack.pop()

            if node not in visited:
                print(node)
                visited.add(node)

                for nodes in reversed(self.graph[node]):
                    if nodes not in visited:
                        stack.append(nodes)

    def print(self):
        print(self.graph)

graph = Graph()
graph.add_nodes('A')
graph.add_nodes('B')
graph.add_nodes('C')
graph.add_nodes('D')
graph.add_edges('A', 'B')
graph.add_edges('A', 'C')
graph.add_edges('B', 'C')
graph.add_edges('C', 'D')
graph.DFS('A')
graph.print()