import unittest
from math import sqrt
import random
from itertools import product
import pygame
from bowyer_watson import BowyerWatson, Vertex, Edge, Triangle
import visualizer


class TestEdge(unittest.TestCase):
    def setUp(self):
        self.v0 = Vertex(0, 0)
        self.v1 = Vertex(1, 0)
        self.v2 = Vertex(0, 1)
        self.v3 = Vertex(-1, 0)
        self.v4 = Vertex(2, 6)
        self.v5 = Vertex(0, 0)
        self.v6 = Vertex(4, 2)
        self.v7 = Vertex(2, 5)
        self.v8 = Vertex(8, 3)
        self.e1 = Edge(self.v1, self.v2)
        self.e1_2 = Edge(self.v2, self.v1)
        self.e2 = Edge(self.v2, self.v3)
        self.e3 = Edge(self.v1, self.v3)
        self.e4 = Edge(self.v4, self.v5)
        self.e4_2 = Edge(self.v5, self.v4)
        self.e5 = Edge(self.v5, self.v6)
        self.e6 = Edge(self.v4, self.v6)
        self.e7 = Edge(self.v7, self.v8)
        self.e8 = Edge(self.v0, self.v1)
        self.e9 = Edge(self.v0, self.v2)

    def test_edge_midpoint(self):
        self.assertEqual(self.e1.get_midpoint(), Vertex(0.5, 0.5))
        self.assertEqual(self.e3.get_midpoint(), Vertex(0, 0))

    def test_edge_slope(self):
        self.assertEqual(self.e1.get_slope(), -1)
        self.assertEqual(self.e1_2.get_slope(), -1)
        self.assertEqual(self.e4.get_slope(), 3)
        self.assertEqual(self.e8.get_slope(), 0)
        self.assertEqual(self.e9.get_slope(), float("inf"))

    def test_edge_pb_slope(self):
        self.assertEqual(self.e1_2.get_pb_slope(), 1)
        self.assertEqual(self.e1.get_pb_slope(), 1)
        self.assertAlmostEqual(self.e4_2.get_pb_slope(), -1/3)
        self.assertAlmostEqual(self.e4.get_pb_slope(), -1/3)
        self.assertEqual(self.e8.get_pb_slope(), float("inf"))
        self.assertEqual(self.e9.get_pb_slope(), 0)

    def test_pb_intercept(self):
        self.assertEqual(self.e7.get_pb_intercept(), -11)
        self.assertEqual(self.e1.get_pb_intercept(), 0)
        self.assertAlmostEqual(self.e4.get_pb_intercept(), 10/3)
        self.assertEqual(self.e8.get_pb_intercept(), 0)
        self.assertEqual(self.e9.get_pb_intercept(), 0.5)

    def test_edge_get_key(self):
        alt_e1 = Edge(self.v2, self.v1)
        self.assertEqual(tuple(sorted((self.v1, self.v2))), self.e1.get_key())
        self.assertEqual(tuple(sorted((self.v1, self.v2))), alt_e1.get_key())


class TestTriangle(unittest.TestCase):
    def setUp(self):
        self.v1 = Vertex(1, 0)
        self.v2 = Vertex(0, 1)
        self.v3 = Vertex(-1, 0)
        self.v4 = Vertex(2, 6)
        self.v5 = Vertex(0, 0)
        self.v6 = Vertex(4, 2)
        self.e1 = Edge(self.v1, self.v2)
        self.e2 = Edge(self.v2, self.v3)
        self.e3 = Edge(self.v1, self.v3)
        self.e4 = Edge(self.v4, self.v5)
        self.e5 = Edge(self.v5, self.v6)
        self.e6 = Edge(self.v4, self.v6)
        self.edges = {  self.e1.get_key(): self.e1,
                        self.e2.get_key(): self.e2,
                        self.e3.get_key(): self.e3,
                        self.e4.get_key(): self.e4,
                        self.e5.get_key(): self.e5,
                        self.e6.get_key(): self.e6,
                    }
        self.tri1 = Triangle(self.v1, self.v2, self.v3, self.edges)
        self.tri2 = Triangle(self.v4, self.v5, self.v6, self.edges)

    def test_triangle_circumcircle_radius(self):
        self.assertAlmostEqual(self.tri1.get_circumcircle_radius(), 1)
        self.assertAlmostEqual(self.tri2.get_circumcircle_radius(), sqrt(10))

    def test_triangle_circumcenter(self):
        self.assertAlmostEqual(self.tri1.get_circumcenter().x, 0)
        self.assertAlmostEqual(self.tri1.get_circumcenter().y, 0)
        self.assertAlmostEqual(self.tri2.get_circumcenter().x, 1)
        self.assertAlmostEqual(self.tri2.get_circumcenter().y, 3)

    def test_triangle_vertex_in_circumcircle(self):
        self.assertEqual(self.tri1.vertex_in_circumcircle(self.v5), True)
        self.assertEqual(self.tri1.vertex_in_circumcircle(self.v4), False)
        self.assertEqual(self.tri2.vertex_in_circumcircle(self.v3), False)
        self.assertEqual(self.tri2.vertex_in_circumcircle(self.v2), True)


class TestBowyerWatson(unittest.TestCase):
    def setUp(self):
        self.bw = BowyerWatson()

        self.hard_points = [(0,0),(1,1),(1,0), (2,0), (1,1), (2,2), (1,1e-12), (2,2e-12),(3,0)]
        self.point_of_difficulty = [(0,0),(1,1),(1,0)] #super tri points are created so that
                                        #points such as these will form a triangle with all
                                        #points on a single line (fixed)

    def get_random_points_float(self, n, min_coords, max_coords):
        return [(random.uniform(min_coords[0], max_coords[0]),
                 random.uniform(min_coords[1], max_coords[1])) for _ in range(n)]

    def get_random_points_int(self, n, min_coords, max_coords):
        return [(random.randint(min_coords[0], max_coords[0]),
                 random.randint(min_coords[1], max_coords[1])) for _ in range(n)]

    def point_in_triangle(self, point, triangle):
        """point in triangle test using barymetric coordinates
        triangle: tuple of three coords"""
        x, y = point
        (x1, y1), (x2, y2), (x3, y3) = triangle
        denominator = ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3))
        if denominator == 0:
            return True
        a = ((y2 - y3)*(x - x3) + (x3 - x2)*(y - y3)) / denominator
        b = ((y3 - y1)*(x - x3) + (x1 - x3)*(y - y3)) / denominator
        c = 1 - a - b
        if 0 <= a <= 1 and 0 <= b <= 1 and 0 <= c <= 1:
            return True
        return False

    def test_hard_points(self):
        self.bw.add_points(self.hard_points)
        self.bw.triangulate_all()
        # print(self.bw.triangles.values())

    def test_random_points_float_runs(self):
        min_coords = (0, 0)
        max_coords = (100, 100)
        n = 10**2
        self.bw.add_points(self.get_random_points_float(n, min_coords, max_coords))
        self.bw.triangulate_all()
        # print(self.bw.triangles.values())

    def test_super_vert_generation_issue_or_circumcenter_logic(self):
        self.bw.add_points(self.point_of_difficulty)
        # print(self.bw.triangles.values())
        self.bw.triangulate_all()
        # print(self.bw.triangles.values())

    def test_full_house(self):
        full_house_points = list(product(range(32), range(32)))
        self.bw.add_points(full_house_points)
        self.bw.triangulate_all()

    def test_found_and_fixed_case_of_forming_1_tri_out_of_4_points(self):
        points = sorted(list(((559, 115), (96, 451), (358, 463), (956, 457))))
        self.bw.add_points(points)
        self.bw.triangulate_all()
        self.assertEqual(len(self.bw.triangles), 2)

    def test_random_4_points_iterated(self):
        i = 10*4
        for i in range(i):
            self.random_4_points_tri_count()

    def random_4_points_tri_count(self):
        n = 4
        min_coords = (random.randint(0,50), random.randint(0,50))
        max_coords = (random.randint(70,1200), random.randint(70,1200))
        points = self.get_random_points_int(n, min_coords, max_coords)
        bw = BowyerWatson(points=points)
        bw.triangulate_all()
        point_inside = False
        for a in points:
            tri = points.copy()
            tri.remove(a)
            if self.point_in_triangle(a, tri):
                point_inside = True
        if point_inside:
            if len(bw.triangles) != 3:
                print(f"point {a} inside {tri}")
                print(f"not 3 when point inside, points: {points}")
                print(f"{len(bw.triangles)} triangles: {bw.triangles.values()}")
            # also accepting a 2 due to some of these being points practically on the line.
            # left the printout so you can visually confirm the test cases if in doubt
            self.assertIn(len(bw.triangles), [2,3],
                          "Triangle count not in [2,3] in a triangulation of 4 points")
        else:
            if len(bw.triangles) != 2:
                print("not 2 when point outside: ", end="")
                print(f"minc{min_coords} maxc{max_coords};\npoints: {points}")
                print(f"{len(bw.triangles)} triangles: {bw.triangles.values()}")
            self.assertEqual(len(bw.triangles), 2,
                    "Triangle count not 2 in what should be a convex triangulation of 4 points")


class TestVisualization(unittest.TestCase):
    def setUp(self):
        self.min_coords = (0, 0)
        self.max_coords = (100, 100)
        surf_size = self.max_coords[0]*2,self.max_coords[1]*2
        dump_surface = pygame.Surface(surf_size)
        self.visual = visualizer.Visualizer(dump_surface)
        self.bw = BowyerWatson(visualizer_queue=self.visual.event_queue)

    def get_random_points_float(self, n, min_coords, max_coords):
        return list(set([(random.uniform(min_coords[0],max_coords[0]),
                 random.uniform(min_coords[1],max_coords[1])) for _ in range(n)]))

    def get_random_points_int(self, n, min_coords, max_coords):
        return [(random.randint(min_coords[0],max_coords[0]),
                 random.randint(min_coords[1],max_coords[1])) for _ in range(n)]

    def test_visualization_triangulation_equality_triangles(self):
        n = 10**2
        points=self.get_random_points_int(n, self.min_coords, self.max_coords)
        self.bw.add_points(points)
        self.bw.triangulate_all()
        self.visual.process_all()
        vis_entities = [ entity.get_bw_key()
            for entity in self.visual.entities.values()
            if entity.__class__ == visualizer.VisualTriangle
        ]
        # for triangle in self.bw.triangles.values():
        #     print(triangle.get_key())
        bw_result = [obj.get_key() for obj in self.bw.triangles.values()]
        # print("common objs:", set(bw_result) & set(vis_entities))
        # print("set_vis:", set(vis_entities))
        self.assertEqual(set(bw_result), set(vis_entities))

    def test_visualization_triangle_count_specific_case(self):
        points = [(342, 163), (664, 272), (259, 111), (239, 284)]
        self.bw.add_points(points)
        self.bw.triangulate_all()
        self.visual.process_all()
        vis_entities = [ entity.get_bw_key()
            for entity in self.visual.entities.values()
            if entity.__class__ == visualizer.VisualTriangle
        ]
        for triangle in self.bw.triangles.values():
            print(triangle.get_key())
        bw_result = [obj.get_key() for obj in self.bw.triangles.values()]
        print("common objs:", set(bw_result) & set(vis_entities))
        print("set_vis:", set(vis_entities))
        self.assertEqual(set(bw_result), set(vis_entities))
