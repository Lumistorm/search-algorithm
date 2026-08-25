import networkx as nx
import matplotlib.pyplot as plt
from collections import deque, Counter
import random


def random_network(node_count, min_neighbors=2, max_neighbors=6):
    if min_neighbors < 2:
        raise ValueError("min_neighbors must be at least 2")

    if max_neighbors < min_neighbors:
        raise ValueError("max_neighbors must be >= min_neighbors")

    if node_count < min_neighbors + 1:
        raise ValueError("Not enough nodes")

    G = nx.Graph()

    positions = {
        node: (random.random(), random.random())
        for node in range(node_count)
    }

    nx.set_node_attributes(G, positions, "pos")
    G.add_nodes_from(range(node_count))

    def distance(a, b):
        ax, ay = positions[a]
        bx, by = positions[b]
        return (ax - bx) ** 2 + (ay - by) ** 2

    distances = {
        node: sorted(
            (other for other in range(node_count) if other != node),
            key=lambda other: distance(node, other)
        )
        for node in range(node_count)
    }

    # Build a connected geometric backbone.
    remaining = set(range(node_count))
    connected = {0}
    remaining.remove(0)

    while remaining:
        best = None

        for node in remaining:
            for other in connected:
                d = distance(node, other)

                if best is None or d < best[0]:
                    best = (d, node, other)

        _, node, other = best

        if G.degree[node] < max_neighbors and G.degree[other] < max_neighbors:
            G.add_edge(node, other)
            connected.add(node)
            remaining.remove(node)
        else:
            # Find another nearby connection.
            candidates = sorted(
                (
                    (distance(node, other), node, other)
                    for other in connected
                    if G.degree[other] < max_neighbors
                )
            )

            if not candidates:
                raise RuntimeError("Could not construct network")

            _, node, other = candidates[0]
            G.add_edge(node, other)
            connected.add(node)
            remaining.remove(node)

    # Add short geometric edges until every node has min_neighbors.
    changed = True

    while changed:
        changed = False

        for node in list(G.nodes):
            while G.degree[node] < min_neighbors:
                candidates = [
                    other
                    for other in distances[node]
                    if (
                        other != node
                        and not G.has_edge(node, other)
                        and G.degree[other] < max_neighbors
                    )
                ]

                if not candidates:
                    raise RuntimeError(
                        "Could not satisfy min_neighbors with max_neighbors"
                    )

                other = candidates[0]
                G.add_edge(node, other)
                changed = True

    # Add additional nearby edges randomly.
    candidates = []

    for a in G:
        for b in distances[a]:
            if a >= b:
                continue

            if G.has_edge(a, b):
                continue

            if G.degree[a] >= max_neighbors:
                continue

            if G.degree[b] >= max_neighbors:
                continue

            candidates.append((distance(a, b), a, b))

    random.shuffle(candidates)
    candidates.sort()

    for _, a, b in candidates:
        if G.degree[a] >= max_neighbors:
            continue

        if G.degree[b] >= max_neighbors:
            continue

        if random.random() < 0.35:
            G.add_edge(a, b)

    return G


def breadth_first_search(graph, start, end):
    explored = set()
    visited = {start}
    queue = deque([(start, [start])])

    while queue:
        node, path = queue.popleft()
        explored.add(node)

        if node == end:
            return path, explored

        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return [], explored


def custom_search(graph, start, end):
    pass


def main():
    shortest_count = 0
    failures = []
    count = 100
    efficiency_avg = 0
    for i in range(count):
        graph = random_network(20)
        # graph = nx.gnp_random_graph(100, 0.1)
        while graph.has_edge(1, 16):
            graph = random_network(20)
            # graph = nx.gnp_random_graph(100, 0.1)
        bfs_path, bfs_explored = breadth_first_search(graph, 1, 16)
        custom_path, custom_explored = custom_search(graph, 1, 16)

        if len(custom_path) == len(bfs_path):
            shortest_count += 1
        else:
            failures.append(len(custom_path)/len(bfs_path))

        efficiency_avg += len(custom_explored) / len(bfs_explored)

        print(i, 'breadth first search:', bfs_path, f'explored={len(bfs_explored)}')
        print(i, 'custom search:', custom_path, f'explored={len(custom_explored)}', f'shortest={'✅' if len(custom_path) == len(bfs_path) else '❌'}')
    efficiency_avg /= count
    print(f'shortest path found: {shortest_count}/{count}')
    print(f'failures: {failures} ratio')
    print(f'efficiency: {efficiency_avg} ratio')


    nx.draw(
        graph,
        with_labels=True,
        node_size=300,
        width=0.5
    )
    plt.show()


if __name__ == '__main__':
    main()
