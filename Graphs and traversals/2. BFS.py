class Graph:
    def __init__(self):
        self.graph = {}

    def add_nodes(self, node):
        if node not in self.graph:
            self.graph[node] = []
        else:
            return "Node already exists."

    def add_edges(self, from_, to_, cost=0):
        self.graph[from_].append(to_)
        # self.graph[from_].append(cost)     No need for cost in BFS, as
        # self.graph[to_].append(from_)  the search is for uninformed pattern

    def BFS(self, start_node):
        queue = [start_node]
        visit = []
        visited = set()
        visited.add(start_node)

        while queue:
            node = queue.pop()
            print(node, end=" ")

            if node == 'D':
                return 'Destination reached.'

            if node in self.graph:
                for neighbor in self.graph[node]:
                    if neighbor not in visited:
                        queue.append(neighbor)
                        visited.add(neighbor)

    def print(self):
        print(self.graph)


graph = Graph()
graph.add_nodes('A')
graph.add_nodes('B')
graph.add_nodes('C')
graph.add_nodes('D')
graph.add_edges('A', 'B')
graph.add_edges('B', 'C')
graph.add_edges('C', 'A')
graph.add_edges('B', 'D')
graph.BFS('A')
# graph.print()
