import unittest
from bowyer_watson import BowyerWatson, Vertex, Edge, Triangle


class TestEdge(unittest.TestCase):
    def setUp(self):
        self.v1 = Vertex(1, 0)
        self.v2 = Vertex(0, 1)
        self.v3 = Vertex(-1, 0)
        self.v4 = Vertex(2, 6)
        self.v5 = Vertex(0, 0)
        self.v6 = Vertex(4, 2)
        self.v7 = Vertex(2, 5)
        self.v8 = Vertex(8, 3)
        self.e1 = Edge(self.v1, self.v2)
        self.e2 = Edge(self.v2, self.v3)
        self.e3 = Edge(self.v1, self.v3)
        self.e4 = Edge(self.v4, self.v5)
        self.e5 = Edge(self.v5, self.v6)
        self.e6 = Edge(self.v4, self.v6)
        self.e7 = Edge(self.v7, self.v8)

    def test_edge_midpoint(self):
        self.assertEqual(self.e1.get_midpoint(), Vertex(0.5, 0.5))
        self.assertEqual(self.e3.get_midpoint(), Vertex(0, 0))

    def test_edge_nr_slope(self):
        self.assertEqual(self.e1.get_nr_slope(), -1)
        self.assertEqual(self.e4.get_nr_slope(), 3)

    def test_edge_intercept(self):
        self.assertEqual(self.e7.get_intercept(), -11)
        self.assertEqual(self.e1.get_intercept(), 1)
        self.assertEqual(self.e4.get_intercept(), 0)

    def test_edge_get_key(self):
        alt_e1 = Edge(self.v2, self.v1)
        self.assertEqual(sorted((self.v1, self.v2)), self.e1.get_key())
        self.assertEqual(sorted((self.v1, self.v2)), alt_e1.get_key())


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
        self.assertEqual(self.tri1.get_circumcircle_radius(), 1)
        self.assertEqual(self.tri2.get_circumcircle_radius(), 3)

    def test_triangle_circumcenter(self):
        self.assertEqual(self.tri1.get_circumcenter(), Vertex(0, 0))
        self.assertEqual(self.tri2.get_circumcenter(), Vertex(1, 3))

    def test_triangle_vertex_in_circumcircle(self):
        self.assertEqual(self.tri1.vertex_in_circumcircle(self.v5), True)
        self.assertEqual(self.tri1.vertex_in_circumcircle(self.v4), False)
        self.assertEqual(self.tri2.vertex_in_circumcircle(self.v3), False)
        self.assertEqual(self.tri2.vertex_in_circumcircle(self.v2), True)


class TestBowyerWatson(unittest.TestCase):
    def setUp(self):
        self.points = []
        self.empty_bw = BowyerWatson(self.points, max_x=100, max_y=100)

    def test_empty_bw(self):
        self.assertEqual(len(self.empty_bw.points), 0)