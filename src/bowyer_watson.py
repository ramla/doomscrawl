from math import sqrt
import config


class BowyerWatson:
    def __init__(self, points, max_x, max_y):
        super_triangle = ((0,0), 
                          (max_x * 2 + 1, 0),
                          (0, max_y * 2 + 1)
                         )
        self.points = points
        self.verts = [super_triangle[0],super_triangle[1],super_triangle[2]]
        self.edges = {
                self.get_edge_key(super_triangle[0], super_triangle[1]): Edge(super_triangle[0],super_triangle[1]),
                self.get_edge_key(super_triangle[0], super_triangle[2]): Edge(super_triangle[0],super_triangle[2]),
                self.get_edge_key(super_triangle[2], super_triangle[1]): Edge(super_triangle[2],super_triangle[1]),
                }
        self.triangles = {
                self.get_triangle_key(super_triangle[0], super_triangle[1], super_triangle[2]): Triangle(super_triangle[0], super_triangle[1], super_triangle[2], self.edges)
                }

    def get_edge_key(vertex_a, vertex_b):
        return sorted((vertex_a, vertex_b))

    def get_triangle_key(vertex_a, vertex_b, vertex_c):
        return sorted((vertex_a, vertex_b, vertex_c))

    def triangulate(self):
        for point in self.points:
            bad_triangles = set()
            for triangle in self.triangles:
                if triangle.vertex_in_circumcircle(triangle, point):
                    bad_triangles.add(triangle)
                    for edge in triangle.get_edges():
                        pass


class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, vertex):
        return self.x == vertex.x and self.y == vertex.y

    def distance_from(self, vertex):
        return sqrt((self.x - vertex.x)**2 + (self.y - vertex.y)**2)


class Edge:
    def __init__(self, vertex_a:Vertex, vertex_b:Vertex):
        self.vertex_a = vertex_a
        self.vertex_b = vertex_b

    def __eq__(self, edge:"Edge"):
        return (self.vertex_a == edge.vertex_a and self.vertex_b == self.vertex_b) \
            or (self.vertex_a == self.vertex_b and self.vertex_b == self.vertex_a)

    def get_key(self):
        return sorted((self.vertex_a, self.vertex_b))

    def get_vertices(self):
        return (self.vertex_a, self.vertex_b)

    def get_midpoint(self):
        if not self.midpoint:
            self.midpoint = Vertex((self.vertex_a[0] + self.vertex_b[0]) / 2, (self.vertex_a[1] + self.vertex_b[1] / 2))
        return self.midpoint

    def get_nr_slope(self):
        """Return the negative reciprocal of the edge's slope"""
        if not self.nr_slope:
            self.nr_slope = -1 / (self.vertex_a[1] + self.vertex_b[1]) / (self.vertex_a[0] + self.vertex_b[0])
        return self.nr_slope

    def get_intercept(self):
        if not self.intercept:
            self.intercept = self.get_midpoint()[1] - (1 / self.get_slope())


class Triangle:
    def __init__(self, vertex_a, vertex_b, vertex_c, edge_lookup):
        self.vertex_a = vertex_a
        self.vertex_b = vertex_b
        self.vertex_c = vertex_c
        self.edge_lookup = edge_lookup

    def get_vertices(self):
        return (self.vertex_a, self.vertex_b, self.vertex_c)

    def get_edges(self):
        return (self.edge_lookup[sorted((self.vertex_a, self.vertex_b))],
                self.edge_lookup[sorted((self.vertex_a, self.vertex_c))],
                self.edge_lookup[sorted((self.vertex_b, self.vertex_c))]
            )

    def get_circumcircle_radius(self):
        if not self.circumcircle_radius:
            a, b, c = self.vertex_a, self.vertex_b, self.vertex_c
            self.circumcircle_radius = a*b*c / sqrt((a+b+c)*(b+c-a)*(c+a-b)*(a+b-c))
        return self.circumcircle_radius

    def get_circumcenter(self):
        """Return circumcenter of the triangle

        Calculated from the intersection of the perpendicular
        bisectors of the triangle's two edges by using the determinant method:

        Lines:
        A_1x + B_1y = C_1
        A_2x + B_2y = C_2
        where B_1 = B_2 = 1
        Determinants:
        D = A1*B2 - A2*B1
        D_x = C1*B2 - C2*B1
        D_y = A1*C2 - A2*C1
        Point:
        x = D_x/D, y = D_y/D

        """
        if not self.circumcenter:
            edge_1, edge_2, _ = self.get_edges()
            a_1 = edge_1.get_nr_slope()
            c_1 = edge_1.get_intercept()
            a_2 = edge_2.get_nr_slope()
            c_2 = edge_2.get_intercept()
            x = (c_1 - c_2) / (a_1 - a_2)
            y = ((a_1 * c_2) - (a_2 * c_1)) / (a_1 - a_2)
            self.circumcenter = Vertex(x,y)
        return self.circumcenter

    def vertex_in_circumcircle(self, vertex):
        return self.get_circumcenter().distance_from(vertex) <= self.get_circumcircle_radius()
