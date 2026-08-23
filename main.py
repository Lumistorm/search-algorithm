import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import random


def random_network(node_count):
    G = nx.Graph()
    G.add_nodes_from(range(node_count))

    while True:
        possible = [
            n for n in G
            if G.degree[n] < 3
        ]

        edges = [
            (a, b)
            for i, a in enumerate(possible)
            for b in possible[i + 1:]
            if not G.has_edge(a, b)
        ]

        if not edges:
            break

        a, b = random.choice(edges)
        G.add_edge(a, b)

    # Ensure every node has at least 1 connection
    for node in G:
        if G.degree[node] == 0:
            candidates = [
                n for n in G
                if n != node and G.degree[n] < 6
            ]

            if candidates:
                G.add_edge(node, random.choice(candidates))

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
    penalties = {}

    queue = deque([(start, [start])])
    explored = set()
    path = []

    while queue:
        current, path = queue.popleft()
        explored.add(current)

        if current == end:
            path.append(end)
            break

        neighbors = list(graph.neighbors(current))

        if end in neighbors:
            path.append(end)
            break

        scores = {}

        for node in neighbors:
            if node in path:
                continue

            degree_score = graph.degree[node] * 0
            penalty = penalties.get(node, 0)

            scores[node] = degree_score - penalty

        if not scores:
            continue

        best_score = max(scores.values())

        candidates = [
            node
            for node, score in scores.items()
            if score == best_score
        ]

        # Update penalties
        for node in penalties:
            penalties[node] *= 0.8

        for node in neighbors:
            penalties[node] = penalties.get(node, 0) + 4

        penalties[current] = penalties.get(current, 0) + 4

        # Add ALL equally-scored nodes to the queue
        for node in candidates:
            queue.append((node, path + [node]))

    return path, explored


def main():
    shortest_count = 0
    failures = []
    count = 100
    efficiency_avg = 0
    for i in range(count):
        # graph = random_network(100)
        graph = nx.gnp_random_graph(100, 0.1)
        while graph.has_edge(1, 16):
            # graph = random_network(100)
            graph = nx.gnp_random_graph(100, 0.1)
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

    pos = nx.spring_layout(graph, k=3, iterations=50)

    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_size=300,
        width=0.5
    )
    plt.show()


if __name__ == '__main__':
    main()
