import unittest
from random import randint, choice
from itertools import combinations
from collections import deque
from utility import get_random_points_int
from prims import prims, Graph

class TestPrims(unittest.TestCase):
    def setUp(self):
        pass

    def get_prims_maximally_connected_random_points(self):
        n = randint(5,5)
        points = list(set(get_random_points_int(n, (100,100), (1100,700))))
        # get every possible unique edge
        combos = [tuple(sorted(combo)) for combo in combinations(points, 2)]
        unique_edges = list(set(combos))
        # give them weights
        weighted_edges = [(a, b, randint(0,10)) for a, b in unique_edges]
        return points, weighted_edges, prims(points, weighted_edges)

    def test_iterate_prims_maximally_connected_points(self):
        """Tests that prims returns trees where every given input point is reachable and
        amount of edges in tree equals to amount of input points -1"""
        for _ in range(10**3):
            points, weighted_edges, minimum_spanning_tree \
                = self.get_prims_maximally_connected_random_points()
            self.assertEqual(len(minimum_spanning_tree), len(points) - 1)

            weighed_mst = set()
            mst_points = set()
            for (a, b, weight) in weighted_edges:
                edge = tuple(sorted((a, b)))
                if [edge[0], edge[1]] in minimum_spanning_tree:
                    mst_points.add(a)
                    mst_points.add(b)
                    weighed_mst.add((a,b,weight))

            mst_graph = Graph(list(mst_points))
            for a, b, weight in weighed_mst:
                mst_graph.edges[a].append((b, weight))
                mst_graph.edges[b].append((a, weight))

            start_node = choice(points)
            self.assertEqual(self.get_reachable_nodes(mst_graph, start_node), set(points))

    def get_reachable_nodes(self, graph, start):
        queue = deque([start])
        visited = set()
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for node, _ in graph.edges[current]:
                queue.append(node)
        return visited
