import unittest
from math import sqrt
import random
from itertools import product
import pygame
from bowyer_watson import BowyerWatson, Vertex, Edge, Triangle
import visualizer
from game import Doomcrawl
from utility import get_random_points_int, get_random_points_float


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
        self.assertEqual(tuple(sorted((self.v1.get_coord(),
                                       self.v2.get_coord()))),
                                       self.e1.get_key())
        self.assertEqual(tuple(sorted((self.v1.get_coord(),
                                       self.v2.get_coord()))),
                                       alt_e1.get_key())


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
        self.bw.add_points(get_random_points_float(n, min_coords, max_coords))
        self.bw.triangulate_all()
        # print(self.bw.triangles.values())

    def test_super_vert_generation_issue_or_circumcenter_logic(self):
        self.bw.add_points(self.point_of_difficulty)
        # print(self.bw.triangles.values())
        self.bw.triangulate_all()
        # print(self.bw.triangles.values())

    def test_full_house(self):
        full_house_points = list(product(range(16), range(16)))
        self.bw.add_points(full_house_points)
        self.bw.triangulate_all()

    def test_found_and_fixed_case_of_forming_1_tri_out_of_4_points(self):
        points = sorted(list(((559, 115), (96, 451), (358, 463), (956, 457))))
        self.bw.add_points(points)
        self.bw.triangulate_all()
        self.assertEqual(len(self.bw.triangles), 2)

    def test_random_4_points_iterated(self):
        its = 0
        limit = 10**3
        exceptions = []
        while its < limit:
            its += 1
            if its % 1000 == 0:
                print("iteration", its)
            exception = self.random_4_points_tri_count()
            if exception:
                exceptions.append(exception)
        i = 0
        visually_confim_test_exceptions = True
        print(exceptions)
        while visually_confim_test_exceptions and i < len(exceptions):
            title, point_set = exceptions[i]
            try:
                app = Doomcrawl(list(zip(point_set, len(point_set)*[(40,40)])),
                                add_title=title, exceptions=True)
                app.start()
            except SystemExit as e:
                if str(e) == "1":
                    visually_confim_test_exceptions = False
            i += 1

    def random_4_points_tri_count(self):
        """This magnificent beast tests triangle counts in triangulations handling relevant edge
        cases. Visual confirmation is available for inspection in nontrivial cases.
        
        - All convex triangulations of 4 points should result in two triangles. Convex is determined
        by checking whether any of the given points lie inside the triangle formed by the other
        three.
        
        - When three points lie close enough to being on the same line, point may be detected
        to lie within the triangle formed by other points but due to non-infinite distance to
        supervertices the result of two triangles is still valid.

        - In four points, one may be rejected due to hitting another triangle's circumcircle's
        perimeter exactly enough => one triangle should be found.
        
        - Points location and order of triangulation may cause the sole edge
        connecting one point to other triangulated points only forms triangles containing
        supervertices, the edge will get removed in the end. For the use case this is handled by
        checking for such edge when removing triangles. This case should result in one triangle
        and four edges.

        - If all points lie close to being on the same line, all triangles may be supervertex-
        connected and be removed at the final phase. Again, this is handled and results in no
        triangles but three edges.
        """

        n = 4
        points = []
        min_coords = (random.randint(0,50), random.randint(0,50))
        max_coords = (random.randint(70,1200), random.randint(70,700))
        while len(set(points)) != 4:
            points = get_random_points_int(n, min_coords, max_coords)
        bw = BowyerWatson(points=points)
        bw.triangulate_all()
        point_inside = False
        for a in points:
            tri = points.copy()
            tri.remove(a)
            if self.point_in_triangle(a, tri):
                point_inside = True
        if bw.rejected_points:
            # since rejected points were found, there should be exactly one triangle in the
            # case of four original points added to triangulate
            self.assertEqual(len(bw.triangles), 1,
                                f"Well I didn't come to think of this edge case: {points}")
                                # times this assertation failed so far: 1
            return ("Point rejected due to being on circumcircle circumference", points)
        if len(bw.triangles) == 1:
            # points location and order of triangulation may cause the sole edge
            # connecting a point to other triangulated points only form triangles containing
            # supervertices and gets removed in the end.
            # for the use case this is handled by checking for such edge when removing triangles
            # thus testing for the appropriate edge count instead
            print(f"ONE TRIANGLE EXCEPTION: {points}")
                #   f"triangles: {bw.triangles.values()}\n"
                #   f"edges: {list(bw.final_edges)}")
            self.assertEqual(len(bw.final_edges), 4,
                        "Edge count not 4 in a triangulation of 4 points resulting in 1 triangle"
                       f"Points: {points}")
            return ("One triangle, four edges", points)
        if point_inside:
            if len(bw.triangles) not in [2,3]:
                print(f"FOURTH POINT INSIDE EXCEPTION: {points}")
                print("Triangle count not 2 or 3 in what should be a concave triangulation of 4"
                        f" points \nPoints: {points}")
                # assuming points align very close to a line (not checked for), three edges
                # are acceptable as well
                self.assertEqual(len(bw.final_edges), 3,
                    "Edge count not 3 in a triangulation of 4 points resulting in 0 triangles"
                    f"Points: {points}")
                return (f"Fourth point inside but tri count is {len(bw.triangles)} (!= 3):", points)
            # also accepting a 2 triangle result due to some of these are points close to being
            # on a line.
            self.assertIn(len(bw.triangles), [2,3])
            if len(bw.triangles) == 2:
                print(f"FOURTH POINT INSIDE EXCEPTION: {points}")
                return (f"Fourth point inside but tri count is {len(bw.triangles)} (!= 3):",
                        points)
            return None
        elif not point_inside and len(bw.triangles) != 2:
            if len(bw.triangles) == 0:
                print(f"FOURTH POINT OUTSIDE EXCEPTION: {points}")
                print("Triangle count not 2 in what should be a convex triangulation of 4 points"
                    f"\nPoints: {points}")
                # points location and order of triangulation may cause the sole edge
                # connecting a point to other triangulated points to only form triangles containing
                # supervertices and gets removed in the end.
                # for the use case this is handled by checking for such edge when removing triangles
                # thus testing for the appropriate edge count instead
                self.assertEqual(len(bw.final_edges), 3,
                        "Edge count not 3 in a triangulation of 4 points resulting in 0 triangles"
                    f"Points: {points}")
                return (f"Fourth point outside but tri count: {len(bw.triangles)} (!= 2):", points)
        self.assertEqual(len(bw.triangles), 2,
                         f"Looks like there's another edge case I didn't consider: {points}")

    def test_no_other_points_inside_circumcircles(self):
        """Get vertices of all triangles, then check that none of the vertices that aren't the
        triangle's own lie within the circumcircle."""
        min_coords = (0, 0)
        max_coords = (100, 100)
        n = int(10**3)
        self.bw.add_points(get_random_points_float(n, min_coords, max_coords))
        self.bw.triangulate_all()
        all_verts = set()
        for triangle in self.bw.triangles.values():
            all_verts.update(triangle.get_vertices())
        self.assertEqual(n - len(self.bw.rejected_points), len(all_verts))
        for triangle in self.bw.triangles.values():
            tri_verts = set(triangle.get_vertices())
            other_verts = all_verts - tri_verts
            for vertex in other_verts:
                self.assertFalse(triangle.vertex_in_circumcircle(vertex))


class TestVisualization(unittest.TestCase):
    def setUp(self):

        self.min_coords = (0, 0)
        self.max_coords = (100, 100)
        surf_size = self.max_coords[0]*2,self.max_coords[1]*2
        dump_surface = pygame.Surface(surf_size)
        self.visual = visualizer.Visualizer(dump_surface, testing=True)
        self.bw = BowyerWatson(visualizer_queue=self.visual.event_queue)

    def test_visualization_triangulation_equality_triangles(self):
        n = 10**2
        points=get_random_points_int(n, self.min_coords, self.max_coords)
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
