import random
import math
import heapq
from collections import deque, Counter
from itertools import count


GRAPH_WIDTH = 650
GRAPH_HEIGHT = 650

NODE_COUNT = 100

MIN_DEGREE = 4
MAX_DEGREE = 7

MIN_DISTANCE = 45
MAX_EDGE_DISTANCE = 190


class Graph:

    def __init__(self):

        self._nodes = {}
        self._edges = {}

    def _add_node(self, node_id, x, y):

        self._nodes[node_id] = (x, y)
        self._edges[node_id] = set()

    def _add_edge(self, a, b):

        if a == b:
            return

        if b in self._edges[a]:
            return

        self._edges[a].add(b)
        self._edges[b].add(a)

    def neighbors(self, node):
        return self._edges[node]

    def degree(self, node):
        return len(self._edges[node])

    def average_degree(self):
        degree_sum = sum(len(neighbors)for neighbors in self._edges.values())

        return degree_sum / len(self._nodes)

    @classmethod
    def generate_graph(cls):
        graph = cls()
        positions = []
        attempts = 0

        # Generate spatially distributed nodes.
        while len(positions) < NODE_COUNT:
            attempts += 1
            if attempts > NODE_COUNT * 10000:
                raise RuntimeError("Could not generate graph.")

            x = random.randint(35, GRAPH_WIDTH - 35)
            y = random.randint(35, GRAPH_HEIGHT - 35)

            valid = True
            for px, py in positions:
                if math.hypot(x - px, y - py) < MIN_DISTANCE:
                    valid = False
                    break

            if valid:
                positions.append((x, y))

        # Add nodes.
        for i, (x, y) in enumerate(positions):
            graph._add_node(i, x, y)

        # Candidate local edges.
        candidates = []
        for a in range(NODE_COUNT):
            for b in range(a + 1, NODE_COUNT):
                x1, y1 = positions[a]
                x2, y2 = positions[b]
                distance = math.hypot(x2 - x1, y2 - y1)
                if distance <= MAX_EDGE_DISTANCE:
                    candidates.append((distance, a, b))

        # Start with short/local connections.
        candidates.sort()
        for distance, a, b in candidates:
            if graph.degree(a) >= MAX_DEGREE:
                continue
            if graph.degree(b) >= MAX_DEGREE:
                continue
            if graph.degree(a) >= MIN_DEGREE and graph.degree(b) >= MIN_DEGREE:
                continue
            graph._add_edge(a, b)

        # Repair minimum degree.
        for node in range(NODE_COUNT):
            while graph.degree(node) < MIN_DEGREE:
                x1, y1 = graph._nodes[node]

                possible = []
                for other in range(NODE_COUNT):
                    if other == node:
                        continue
                    if other in graph._edges[node]:
                        continue
                    if graph.degree(other) >= MAX_DEGREE:
                        continue

                    x2, y2 = graph._nodes[other]
                    distance = math.hypot(x2 - x1, y2 - y1)
                    if distance <= MAX_EDGE_DISTANCE:
                        possible.append((distance, other))

                if not possible:
                    break

                possible.sort()
                top = possible[:min(8, len(possible))]
                _, other = random.choice(top)
                graph._add_edge(node, other)

        # A few extra local edges.
        random.shuffle(candidates)
        for distance, a, b in candidates:
            if graph.degree(a) >= MAX_DEGREE:
                continue
            if graph.degree(b) >= MAX_DEGREE:
                continue
            if b in graph._edges[a]:
                continue
            if random.random() < 0.08:
                graph._add_edge(a, b)

        return graph


def breadth_first_search(graph, start, end):
    if start == end:
        return [start], 0

    visited = {start}
    parent = {start: None}
    queue = deque([start])
    nodes_explored = 0

    while queue:
        node = queue.popleft()
        nodes_explored += 1

        for neighbor in graph.neighbors(node):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = node

            if neighbor == end:
                path = [neighbor]
                while parent[path[-1]] is not None:
                    path.append(parent[path[-1]])
                path.reverse()
                return path, nodes_explored

            queue.append(neighbor)

    return [], nodes_explored


def heuristic_search(graph, start, end):
    explored = set()
    visited = {start}
    known = set()

    queue_counter = count()

    # (priority, insertion_order, cost, node, path)
    queue = [
        (0, next(queue_counter), 0, start, [start])
    ]

    while queue:
        priority, _, cost, node, path = heapq.heappop(queue)

        if node in explored:
            continue

        explored.add(node)

        if node == end:
            return path, explored

        neighbors = set(graph.neighbors(node))

        for neighbor in neighbors:
            if neighbor in visited:
                continue

            visited.add(neighbor)

            if neighbor == end:
                return path + [neighbor], explored

            # Direct unexplored opportunities
            new_cost = cost + 1

            overlap = len(set(graph.neighbors(neighbor)) & set(graph.neighbors(node)))

            unseen = len(set(graph.neighbors(neighbor)) - visited)

            degree = graph.degree[neighbor]

            new_priority = (
                    new_cost * 2
                    - unseen * 3
                    - degree
                    + overlap
            )

            heapq.heappush(
                queue,
                (
                    new_priority,
                    next(queue_counter),
                    new_cost,
                    neighbor,
                    path + [neighbor]
                )
            )

    return [], explored


START = 0
END = 99


def main():
    graph = Graph.generate_graph()
    path, total_path_length = breadth_first_search(graph, START, END)
    print(f'=== Breadth First Search ===')
    print(f'path: {path}')
    print(f'path length : {len(path) - 1}')
    print(f'total length : {total_path_length}')
    print('-' * 30)


if __name__ == '__main__':
    main()
