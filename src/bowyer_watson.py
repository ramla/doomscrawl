from math import sqrt
from operator import methodcaller
from collections import deque
import config

class BowyerWatson:
    """Class implements Delaunay triangulation with Bowyer-Watson algorithm. It can be run one
    point at a time to run visualisation in between to see the algorithm at work.

    Attributes:
        points: All points passed to the triangulation class

        next_points: A deque of new tuples of x,y coordinates to triangulate

        super_verts: Tuple containing boundary vertices

        super_tri_key:

        edges: Dictionray containing Edge objects relevant to triangulation

        triangles: Dictionary containing Triangle objects relevant to triangulation

        triangles_with_edge: Dictionary containing count of Triangles in self.triangles that share
            the Edge in key

        intialised: Bool for whether the boundary has been set and points added to next_points

        ready: Bool for readiness to receive next set of points
    """

    def __init__(self, visualizer_queue=None, points=None):
        """
        Parameters:
            visualizer_queue: An optional queue.Queue to put methodcaller objects in with a Vertex,
            Edge or Triangle object and possibly additional parameters. See also visualizer.py

            points: a list of tuples of x,y coordinates
        """
        self.visualizer_queue = visualizer_queue
        self.points = []
        self.next_points = deque()
        self.super_verts = None
        self.super_tri_key = None
        self.edges = {}
        self.triangles = {}
        self.triangles_with_edge = {}
        self.ready = True
        self.add_points(points)

    def add_points(self, points):
        """Initialises the triangulation by creating the boundary around the points and preventing
        further point additions before these have been triangulated

        Parameters:
            points: a list of tuples of x and y coordinates
        """
        if points and self.ready:
            self.next_points.extend(list(set(points)))
            self.points = list(set(self.points + points))
            self.create_super_tri()
            self.ready = False

    def triangulate_point(self, point):
        """Single point triangulation. Simply iterates through existing triangles to find if their
        circumcircle encompasses the given point. Bad triangles are removed and the edges around
        their connected area are used to form new triangles with the new point.
        
        Parameters:
            point: tuple of x,y coordinates expected to lie within the boudaries
        """
        new_vertex = Vertex(point[0],point[1])
        bad_triangles = set()
        self.visualize_new(new_vertex, active=True, reset_active=True)
        for triangle in self.triangles.values():
            if triangle.vertex_in_circumcircle(new_vertex):
                triangle.visualize_circle(self.visualizer_queue)
                bad_triangles.add(triangle)
                for edge in triangle.get_edges():
                    if not edge.get_key() in self.edges:
                        self.edges[edge.get_key()] = edge
                    self.visualize_new(edge, active=True, reset_active=True)
                    self.visualize_activate(triangle)
                triangle.visualize_remove_circle(self.visualizer_queue)
        bad_tri_edgecount = {}
        for triangle in bad_triangles:
            for edge in triangle.get_edges():
                key = edge.get_key() 
                if not key in bad_tri_edgecount:
                    bad_tri_edgecount[key] = 0
                bad_tri_edgecount[key] += 1
                self.visualize_new(edge, active=True, reset_active=True)
        polygon = [self.edges[key] for key, count in bad_tri_edgecount.items() if count == 1]
        for edge in polygon:
            self.visualize_new(edge, active=True)
        for triangle in bad_triangles:
            self.remove_triangle(triangle)
        for edge in polygon:
            vertex_a, vertex_b = edge.get_vertices()
            if self.is_valid_triangle(vertex_a, vertex_b, new_vertex):
                self.add_triangle(vertex_a, vertex_b, new_vertex)

    def iterate_once(self):
        try:
            point = self.next_points.popleft()
            self.triangulate_point(point)
        except IndexError:
            # print("finishing triangulation")
            self.remove_super_tri()
            self.ready = True

    def triangulate_all(self):
        while self.next_points:
            point = self.next_points.popleft()
            self.triangulate_point(point)
        self.remove_super_tri()

    def create_super_tri(self):
        if self.points:
            if self.super_verts is None:
                self.super_verts = self.get_super_vertices()
                super_edges = ( Edge(self.super_verts[0], self.super_verts[1]),
                                Edge(self.super_verts[1], self.super_verts[2]),
                                Edge(self.super_verts[0], self.super_verts[2])
                            )
                for edge in super_edges:
                    self.edges[edge.get_key()] = edge
                self.super_tri_key = self.add_triangle(*self.super_verts)
            else:
                self.grow_super_triangle()
                self.visualize_new(self.triangles[self.super_tri_key])
        if self.visualizer_queue:
            for vertex in self.super_verts:
                self.visualize_new(vertex)

    def get_super_vertices(self):
        margin = config.super_tri_margin
        xs, ys = zip(*self.points)
        min_x, min_y, max_x, max_y = min(xs), min(ys), max(xs), max(ys)
        min_any, max_any = min(min_x, min_y), max(max_x, max_y)
        vertex_a = Vertex(min_any - margin, min_any - margin)
        vertex_b = Vertex(min_any - margin, max_any*2 + margin)
        vertex_c = Vertex(max_any*2 + margin, min_any - margin)
        return (vertex_a, vertex_b, vertex_c)

    def remove_super_tri(self):
        for triangle in list(self.triangles.values()):
            for super_vertex in self.super_verts:
                #visualise super vertex?
                if super_vertex in triangle.get_vertices():
                    if triangle.get_key() != self.super_tri_key:
                        self.visualize_remove(triangle)
                        # self.remove_triangle(triangle)
            self.visualize_remove(super_vertex)

    def add_triangle(self, vertex_a, vertex_b, vertex_c):
        triangle = Triangle(vertex_a, vertex_b, vertex_c, self.edges)
        self.triangles[triangle.get_key()] = triangle
        edges = (Edge(vertex_a, vertex_b),
                 Edge(vertex_a, vertex_c),
                 Edge(vertex_b, vertex_c)
                )
        for edge in edges:
            key = edge.get_key()
            self.edges[key] = edge
            if key not in self.triangles_with_edge:
                self.triangles_with_edge[key] = 0
            self.triangles_with_edge[key] += 1
        self.visualize_new(triangle)
        return triangle.get_key()

    def remove_triangle(self, triangle):
        if not triangle.get_key() in self.triangles:
            return triangle
        self.triangles.pop(triangle.get_key())
        edges = triangle.get_edges()
        for edge in edges:
            key = edge.get_key()
            self.edges[key] = edge
            self.triangles_with_edge[key] -= 1
            if self.triangles_with_edge[key] == 0:
                try:
                    self.visualize_remove(edge)
                except KeyError:
                    if config.visualizer_debug:
                        print("bw.KeyError:",edge)
        self.visualize_remove(triangle)

        #visualise (bad, parameter?) triangle removal

    def visualize_remove(self, bw_object):
        if self.visualizer_queue:
            if isinstance(bw_object, Vertex):
                self.visualizer_queue.put(methodcaller("remove_vertex", bw_object))
            elif isinstance(bw_object, Edge):
                self.visualizer_queue.put(methodcaller("remove_edge", bw_object))
            elif isinstance(bw_object, Triangle):
                self.visualizer_queue.put(methodcaller("remove_triangle", bw_object))

    def visualize_new(self, bw_object, active=False, reset_active=False):
        if self.visualizer_queue: 
            if isinstance(bw_object, Vertex):
                self.visualizer_queue.put(methodcaller("new_vertex", bw_object, active, reset_active))
            elif isinstance(bw_object, Edge):
                self.visualizer_queue.put(methodcaller("new_edge", bw_object, active, reset_active))
            elif isinstance(bw_object, Triangle):
                self.visualizer_queue.put(methodcaller("new_triangle", bw_object, active, reset_active))

    def visualize_activate(self, bw_object, reset_active=False):
        if self.visualizer_queue:
            if isinstance(bw_object, Vertex):
                self.visualizer_queue.put(methodcaller("activate_vertex", bw_object, reset_active))
            elif isinstance(bw_object, Edge):
                self.visualizer_queue.put(methodcaller("activate_edge", bw_object, reset_active))
            elif isinstance(bw_object, Triangle):
                self.visualizer_queue.put(methodcaller("activate_triangle", bw_object, reset_active))

    def is_valid_triangle(self, vertex_a, vertex_b, vertex_c):
        return vertex_a != vertex_b and vertex_b != vertex_c and vertex_a != vertex_c

    def grow_super_triangle(self):
        new_vertices = self.get_super_vertices()
        for i in range(3):
            self.super_verts[i].x, self.super_verts[i].y = new_vertices[i].x, new_vertices[i].y

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

    def get_coord(self):
        return (self.x, self.y)

    def distance_from(self, vertex):
        return sqrt((self.x - vertex.x)**2 + (self.y - vertex.y)**2)


class Edge:
    def __init__(self, vertex_a:Vertex, vertex_b:Vertex):
        self.vertex_a = vertex_a
        self.vertex_b = vertex_b
        self.midpoint = None
        self.slope = None
        self.pb_slope = None
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
            self.midpoint = Vertex((self.vertex_a.x + self.vertex_b.x) / 2,
                                   ((self.vertex_a.y + self.vertex_b.y) / 2))
        return self.midpoint

    def get_slope(self):
        if not self.slope:
            nominator = self.vertex_a.y - self.vertex_b.y
            denominator = self.vertex_a.x - self.vertex_b.x
            if denominator == 0:
                nominator = self.vertex_b.y - self.vertex_a.y
                denominator = self.vertex_b.x - self.vertex_a.x
                if denominator == 0:
                    self.slope = float("inf")
                    return self.slope
            self.slope = nominator / denominator
        return self.slope

    def get_pb_slope(self):
        """Return the negative reciprocal of the edge's slope, which is the
        perpendicular bisector's slope"""
        if not self.pb_slope:
            if not self.slope:
                self.get_slope()
            if self.get_slope() == 0:
                self.pb_slope = float("inf")
            else:
                self.pb_slope = -1 / self.get_slope()
        return self.pb_slope

    def get_pb_intercept(self):
        """Return the y-intercept of the perpendicular bisector of the edge"""
        if not self.pb_intercept:
            slope = self.get_slope()
            midpoint = self.get_midpoint()
            if slope == 0:
                self.pb_intercept = midpoint.y
            else:
                self.pb_intercept = midpoint.y - midpoint.x * self.get_pb_slope()
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
            a, b, c = [edge.get_length() for edge in self.get_edges()]
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
            edges = self.select_edges_for_circumcenter_f()
            a_1 = edges[0].get_pb_slope()
            c_1 = edges[0].get_pb_intercept()
            a_2 = edges[1].get_pb_slope()
            c_2 = edges[1].get_pb_intercept()
            det = a_1 - a_2
            if det == 0:
                print("HELP!!!!!!!!!!!!")
                print("verts",{self.get_vertices()})
                #fails when points are in a straight line
                #need to adjust super verts if this happens?
                #(verts {(Vertex(-50, 70), Vertex(70, -50), Vertex(10, 10))})
            x = (c_2 - c_1) / det
            y = ((a_1 * c_2) - (a_2 * c_1)) / det
            self.circumcenter = Vertex(x,y)
        return self.circumcenter

    def vertex_in_circumcircle(self, vertex):
        return self.get_circumcenter().distance_from(vertex) <= self.get_circumcircle_radius()

    def select_edges_for_circumcenter_f(self):
        """Edges with perpendicular bisectors on lines of form y = 0x + c will be omitted"""
        edges = self.get_edges()
        valid_edges = []
        for edge in edges:
            if edge.get_pb_slope() == float("inf") or edge.get_pb_slope() == float("-inf"):
                continue
            valid_edges.append(edge)
        return valid_edges

    def visualize_circle(self, visualizer_queue):
        if visualizer_queue is not None:
            visualizer_queue.put(methodcaller("new_circle", self))

    def visualize_remove_circle(self, visualizer_queue):
        if visualizer_queue is not None:
            visualizer_queue.put(methodcaller("remove_circle", self))

    def get_circumcircle_key(self):
        return "VCCir" + str(self)
