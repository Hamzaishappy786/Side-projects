class Graph:
    def __init__(self):
        self.graph = {}

    def add_nodes(self, node):
        self.graph[node] = []

    def add_edges(self, from_, to_, cost=0):
        if from_ not in self.graph:
            self.add_nodes(from_)
        elif to_ not in self.graph:
            self.add_nodes(to_)
        self.graph[from_].append((to_, cost))


    def UCS(self, start_node):
        priority_queue = [(0, start_node)]
        visited = set()
        cost = 0
        while priority_queue:
            cost, node = min(priority_queue)
            priority_queue.pop(0)     # in this method, remove is used for tuples of lists

            if node not in visited:
                print(f'Visiting {node} with cost: {cost}')
                visited.add(node)

                if node == 'D':
                    print('Goal reached')
                    return

                for neighbor, edge_cost in self.graph[node]:
                    if neighbor not in visited:
                        priority_queue.append((cost + edge_cost, neighbor))


    def print(self):
        print(self.graph)

graph = Graph()
graph.add_nodes('A')
graph.add_nodes('B')
graph.add_nodes('C')
graph.add_nodes('D')
graph.add_edges('A', 'B', 20)
graph.add_edges('A', 'C', 20)
graph.add_edges('B', 'C', 10)
graph.add_edges('C', 'D', 5)
graph.UCS('A')