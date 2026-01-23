from math import sqrt
import config


class BowyerWatson:
    def __init__(self, points, max_x, max_y):
        self.points = points
        super_verts = ( Vertex(0,0), 
                        Vertex(max_x * 2 + 1, 0),
                        Vertex(0, max_y * 2 + 1)
                    )
        super_edges = (Edge(super_verts[0], super_verts[1]),
                            Edge(super_verts[1], super_verts[2]),
                            Edge(super_verts[0], super_verts[2])
                        )
        self.edges = {
                super_edges[0].get_key(): super_edges[0],
                super_edges[1].get_key(): super_edges[1],
                super_edges[2].get_key(): super_edges[2]
                }
        self.super_triangle = Triangle(super_verts[0], super_verts[1], super_verts[2], self.edges)
        self.verts = []
        self.verts.append(self.super_triangle.get_vertices())
        self.triangles = {self.super_triangle.get_key(): self.super_triangle}

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

    def __lt__(self, vertex):
        if self.x < vertex.x:
            return True
        elif self.x > vertex.x:
            return False
        else:
            return self.y < vertex.y
    
    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Vertex({self.x}, {self.y})"

    def distance_from(self, vertex):
        return sqrt((self.x - vertex.x)**2 + (self.y - vertex.y)**2)


class Edge:
    def __init__(self, vertex_a:Vertex, vertex_b:Vertex):
        self.vertex_a = vertex_a
        self.vertex_b = vertex_b
        self.midpoint = None
        self.slope = None
        self.nr_slope = None
        self.pb_intercept = None
        self.length = None

    def __repr__(self):
        return f"Edge{self.get_key()}"

    def __eq__(self, edge:"Edge"):
        return (self.vertex_a == edge.vertex_a and self.vertex_b == edge.vertex_b) \
            or (self.vertex_a == edge.vertex_b and self.vertex_b == edge.vertex_a)

    def get_key(self):
        return tuple(sorted((self.vertex_a, self.vertex_b)))

    def get_vertices(self):
        return (self.vertex_a, self.vertex_b)

    def get_midpoint(self):
        if not self.midpoint:
            self.midpoint = Vertex((self.vertex_a.x + self.vertex_b.x) / 2, ((self.vertex_a.y + self.vertex_b.y) / 2))
        return self.midpoint

    def get_slope(self):
        if not self.slope:
            nominator = (self.vertex_a.y - self.vertex_b.y)
            denominator = (self.vertex_a.x - self.vertex_b.x)
            if denominator == 0:
                nominator = (self.vertex_b.y - self.vertex_a.y)
                denominator = (self.vertex_b.x - self.vertex_a.x)
                if denominator == 0:
                    self.slope = float("inf")
                    return self.slope
            self.slope = nominator / denominator
        return self.slope

    def get_pb_slope(self):
        """Return the negative reciprocal of the edge's slope, which is the
        perpendicular bisector's slope"""
        if not self.nr_slope:
            if not self.slope:
                self.get_slope()
            if self.get_slope() == 0:
                self.nr_slope = 0
            else:
                self.nr_slope = -1 / self.get_slope()
        return self.nr_slope

    def get_pb_intercept(self):
        """Return the y-intercept of the perpendicular bisector of the edge"""
        if not self.pb_intercept:
            self.pb_intercept = self.get_midpoint().y - self.get_midpoint().x * self.get_pb_slope()
        return self.pb_intercept

    def get_length(self):
        if not self.length:
            self.length = self.vertex_a.distance_from(self.vertex_b)
        return self.length

class Triangle:
    def __init__(self, vertex_a, vertex_b, vertex_c, edge_lookup):
        self.vertex_a = vertex_a
        self.vertex_b = vertex_b
        self.vertex_c = vertex_c
        self.edge_lookup = edge_lookup
        self.circumcenter = None
        self.circumcircle_radius = None

    def __repr__(self):
        return  f"Triangle{self.vertex_a}{self.vertex_b}{self.vertex_c}"

    def get_vertices(self):
        return (self.vertex_a, self.vertex_b, self.vertex_c)

    def get_key(self):
        return tuple(sorted((self.vertex_a, self.vertex_b, self.vertex_c)))

    def get_edges(self):
        return (self.edge_lookup[tuple(sorted((self.vertex_a, self.vertex_b)))],
                self.edge_lookup[tuple(sorted((self.vertex_a, self.vertex_c)))],
                self.edge_lookup[tuple(sorted((self.vertex_b, self.vertex_c)))]
            )

    def get_circumcircle_radius(self):
        if not self.circumcircle_radius:
            sides = []
            for edge in self.get_edges():
                sides.append(edge.get_length())
            a, b, c = sides
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
            edge_1, edge_2, edge_3 = self.get_edges()
            a_1 = edge_1.get_pb_slope()
            c_1 = edge_1.get_pb_intercept()
            a_2 = edge_2.get_pb_slope()
            c_2 = edge_2.get_pb_intercept()
            det = a_1 - a_2
            if det == 0:
                a_1 = edge_3.get_slope()
                c_1 = edge_3.get_pb_intercept()
                det = a_1 - a_2
            x = (c_2 - c_1) / det
            y = ((a_1 * c_2) - (a_2 * c_1)) / det
            self.circumcenter = Vertex(x,y)
        return self.circumcenter

    def vertex_in_circumcircle(self, vertex):
        return self.get_circumcenter().distance_from(vertex) <= self.get_circumcircle_radius()
