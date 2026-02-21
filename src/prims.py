from random import choice
import heapq

def prims(points, edges, start_at=None):
    """A Prim's implementation that expects a connected undirected graph. If an unconnected graph
    is used as input, function will eventually raise an IndexError due to trying to heappop from
    an empty queue.

    Parameters:
        points: list of unique values for nodes

        edges: list of tuples in format of (node_a, node_b, weight)

        start_at: optional node to start at
    """
    if len(edges) < 1:
        return []
    visited = set()
    mst_edges = []
    graph = Graph(points)
    for edge in edges:
        a, b, weight = edge
        graph.add_edge(a, b, weight)
    if start_at is None:
        start_at = choice(graph.nodes)
    reachable = []
    for edge in graph.edges[start_at]:
        weight, b = edge
        heapq.heappush(reachable, (weight, b, start_at))
    while len(visited) != len(graph.nodes):
        _, node, prev = heapq.heappop(reachable)
        if node not in visited:
            for edge in graph.edges[node]:
                w, b = edge
                if b not in visited:
                    heapq.heappush(reachable, (w, b, node))
            visited.add(node)
            mst_edges.append(sorted((node, prev)))
    return mst_edges


class Graph:
    def __init__(self, nodes):
        self.nodes = nodes
        self.edges = {node: [] for node in nodes}

    def add_edge(self, a, b, weight):
        self.edges[a].append((weight, b))
        self.edges[b].append((weight, a))
