import networkx as nx
import matplotlib.pyplot as plt
import heapq
from collections import deque, Counter
from itertools import count


def random_geometric_network(
    node_count=100,
    radius=0.2
):
    while True:
        G = nx.random_geometric_graph(
            node_count,
            radius=radius,
            dim=2,
            p=2
        )

        if nx.is_connected(G):
            return G


def bfs(graph, start, end):
    explored = set()
    visited = {start}

    queue = deque([(start, [start])])

    while queue:
        node, path = queue.popleft()
        explored.add(node)

        if node == end:
            return path, explored

        for neighbor in graph.neighbors(node):
            if neighbor in visited:
                continue

            visited.add(neighbor)

            if neighbor == end:
                return path + [neighbor], explored
            queue.append((neighbor, path + [neighbor]))

    return [], explored


def heuristic_search(graph, start, end):
    explored = set()
    visited = {start}

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

def compare_targets(graph, start=0):
    results = []

    for target in graph.nodes:
        if target == start:
            continue

        bfs_path, bfs_seen = bfs(graph, start, target)
        h_path, h_seen = heuristic_search(graph, start, target)

        if not bfs_path or not h_path:
            continue

        bfs_explored = len(bfs_seen)
        h_explored = len(h_seen)

        results.append({
            "target": target,
            "distance": len(bfs_path) - 1,
            "bfs": bfs_explored,
            "heuristic": h_explored,
            "ratio": h_explored / bfs_explored,
            "bfs_path": len(bfs_path) - 1,
            "heuristic_path": len(h_path) - 1,
        })

    results.sort(key=lambda x: x["distance"])

    print("\n===== BY TARGET DISTANCE =====")

    for r in results:
        print(
            f"distance={r['distance']:2} "
            f"target={r['target']:3} "
            f"BFS={r['bfs']:3} "
            f"H={r['heuristic']:3} "
            f"ratio={r['ratio']:.2f} "
            f"H_path={r['heuristic_path']:2}"
        )

    print("\n===== SUMMARY BY DISTANCE =====")

    distances = sorted(set(r["distance"] for r in results))

    for distance in distances:
        group = [
            r for r in results
            if r["distance"] == distance
        ]

        avg_bfs = sum(r["bfs"] for r in group) / len(group)
        avg_h = sum(r["heuristic"] for r in group) / len(group)
        avg_ratio = sum(r["ratio"] for r in group) / len(group)

        print(
            f"distance={distance:2} "
            f"targets={len(group):2} "
            f"BFS={avg_bfs:6.2f} "
            f"H={avg_h:6.2f} "
            f"ratio={avg_ratio:.2f}"
        )


G = random_geometric_network(
    node_count=100,
    radius=0.2
)

compare_targets(G, 0)

# pos = nx.spring_layout(G, seed=1)
#
# labels = {
#     node: G.degree[node]
#     for node in G
# }
#
# nx.draw(
#     G,
#     pos=pos,
#     node_size=100,
#     labels=labels,
#     with_labels=True
# )
#
# plt.show()