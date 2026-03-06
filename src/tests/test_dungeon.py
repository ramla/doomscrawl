
import unittest
from collections import deque
from dungeon import Dungeon
import config
from bowyer_watson import BowyerWatson
from prims import prims
from astar import AStar

class TestDungeon(unittest.TestCase):
    def setUp(self):
        self.dungeon = Dungeon()

    def test_room_generation(self):
        # one room should be generated in Dungeon init
        self.assertEqual(len(self.dungeon.rooms), 1)
        for _ in range(60): # try randomising 60 more rooms. 60 rooms are not expected to fit
            # inside boundaries but at least there should be plenty to work on
            self.dungeon.add_room()
        self.assertGreater(len(self.dungeon.rooms), 1)
        # each room should have config.room_margin space between any other room (and a whole margin*margin square at the corners)
        for room_a in self.dungeon.rooms.values():
            for room_b in self.dungeon.rooms.values():
                if room_a != room_b:
                    margin_delta = config.room_margin
                    position_delta = ((room_b.x - margin_delta) - room_a.x, (room_b.y - margin_delta) - room_a.y)
                    b_mask = room_b.mask # mask with margin added on each side
                    overlap = room_a.get_mask_with_margin(0).overlap(b_mask, position_delta)
                    rooms_overlap = bool(overlap)
                    self.assertFalse(rooms_overlap)

class TestAStar(unittest.TestCase):
    def setUp(self):
        self.dungeon = Dungeon()
        for _ in range(60):
            self.dungeon.add_room()
        points = self.dungeon.get_room_centers()
        bw = BowyerWatson(points=points)
        bw.triangulate_all()
        mst_edges = self.get_pruned_edges(bw.final_edges)
        self.dungeon.create_corridors(mst_edges)

        self.standalone_astar = AStar({})

    def test_astar_connects_all_rooms(self):
        grid = self.dungeon.astar.grid
        room_and_corridor_nodes = []
        all_nodes = []
        edges = []
        start_node = None
        grid_y_max = len(grid) - 1
        grid_x_max = len(grid[0]) - 1
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                node = (x, y)
                all_nodes.append(node)
                if grid[y][x] in (float("inf"), 0):
                    if start_node is None:
                        start_node = node
                    room_and_corridor_nodes.append(node)
                    n_legal = 0 <= y -1 <= grid_y_max
                    e_legal = 0 <= x +1 <= grid_x_max
                    s_legal = 0 <= y +1 <= grid_y_max
                    w_legal = 0 <= x -1 <= grid_x_max
                    edges.append((node, n_legal * (x, y - 1)))
                    edges.append((node, e_legal * (x + 1, y)))
                    edges.append((node, s_legal * (x, y + 1)))
                    edges.append((node, w_legal * (x - 1, y)))
                print((grid[y][x] in (0, float("inf"))) * "X" + (grid[y][x] not in (0, float("inf"))) * " ", end="")
            print("")

        graph = Graph(all_nodes, edges)
        reachable_nodes = self.get_reachable_nodes(graph, start_node, grid)
        self.assertEqual(len(room_and_corridor_nodes), len(reachable_nodes))

    def get_reachable_nodes(self, graph, start, grid):
        queue = deque([start])
        visited = set()
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for node in graph.edges[current]:
                if (grid[node[1]][node[0]] in (0, float("inf"))):
                    queue.append(node)
        return visited

    def get_pruned_edges(self, bw_edges, start_at=None):
        """This is how prims is called. Coords are extracted from the edges and edge lengths are
        got for weights. Prims returns a list of edges in the format of sorted tuples of two
        coords, which are then used to filter relevant edge objects back from input list.
        """
        nodes = set()
        edges = []
        for edge in bw_edges:
            a, b = edge.get_coords()
            weight = edge.get_length()
            nodes.update([a,b])
            edges.append((a, b, weight))
        mst = prims(list(nodes), edges, start_at=start_at)
        mst = [tuple(sorted(x)) for x in mst]
        edge_objects = [edge for edge in bw_edges if edge.get_coords() in mst]
        return edge_objects

    def test_astar_path_length(self):
        self.standalone_astar.grid = [[8,8,8,1,1,1,1,1,1,1,1,1],
                                      [8,8,8,1,1,8,8,8,1,1,1,1],
                                      [1,1,1,1,1,8,8,8,1,1,1,1],
                                      [1,1,1,1,1,8,8,8,1,1,8,8],
                                      [1,1,1,1,1,8,8,8,1,1,8,8],
                                      [1,1,1,1,1,8,8,8,1,1,8,8],
                                      [1,1,1,1,1,8,8,8,1,1,1,1],
                                      [1,1,1,1,1,1,1,1,1,1,1,1]]
        for y in range(len(self.standalone_astar.grid)):
            for x in range(len(self.standalone_astar.grid[0])):
                # replace visually nicer placeholder eights with actual room cell weight
                if self.standalone_astar.grid[y][x] == 8:
                    self.standalone_astar.grid[y][x] = float("inf")
        start, goal = (1,2), (9,4) # x,y
        path = self.standalone_astar.get_path(start, goal, grid_coords=True)
        # shortest path to goal including start and goal cells is 15 in length via north
        self.assertEqual(len(path), 15)
        # if astar took the route above the middle room the cell there was changed to weight 0
        self.assertEqual(self.standalone_astar.grid[0][7], 0)

        self.standalone_astar.grid = [[8,8,8,1,1,1,1,1,1,1,1,1],
                                      [8,8,8,1,1,8,8,8,8,8,8,1],
                                      [1,1,1,1,1,8,8,8,1,1,1,1],
                                      [1,1,1,1,1,8,8,8,1,1,8,8],
                                      [1,1,1,1,1,8,8,8,1,1,8,8],
                                      [1,1,1,1,1,8,8,8,1,1,8,8],
                                      [1,1,1,1,1,8,8,8,1,1,1,1],
                                      [1,1,1,1,1,1,1,1,1,1,1,1]]
        for y in range(len(self.standalone_astar.grid)):
            for x in range(len(self.standalone_astar.grid[0])):
                # replace visually nicer placeholder eights with actual room cell weight
                if self.standalone_astar.grid[y][x] == 8:
                    self.standalone_astar.grid[y][x] = float("inf")
        path = self.standalone_astar.get_path(start, goal, grid_coords=True)
        # shortest path is now via south, 17 in length via north
        self.assertEqual(len(path), 17)
        # took the route below the middle room
        self.assertEqual(self.standalone_astar.grid[7][7], 0)

class Graph:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = {node: [] for node in nodes}
        for edge in edges:
            self.add_edge(edge[0], edge[1])

    def add_edge(self, a, b):
        self.edges[a].append((b))
        self.edges[b].append((a))
