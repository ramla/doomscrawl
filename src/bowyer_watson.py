from math import sqrt, isclose
from operator import methodcaller
from collections import deque
import config

class BowyerWatson:
    """Class implements Delaunay triangulation with Bowyer-Watson algorithm. It can be run one
    point at a time to run visualisation in between to see the algorithm at work.

    Attributes:
        next_points: A deque of new tuples of x,y coordinates to triangulate

        rejected_points: list of points rejected due to being too close to hitting a
        circumference of an existing triangle's circumcircle

        next_points: a deque of points to be triangulated

        point_pushed_back: when a point has been found too close to a circle's perimeter this bool
        is used to cancel the existing recursion stack

        point_tries: dict to keep track of how many times a point has been tried to triangulate
        but failed to not hit the circumcircle of an existing triangle

        super_verts = tuple containing supertriangle's points as Vertex

        super_tri_key: key with which supertriangle is saved in triangles-dictionary

        edges: Dictionray containing Edge objects relevant to triangulation

        bounding_edges: set of edges not containing supervertices, collected when removing
        super connected triangles in the finalising step

        final_edges: the edges connecting the triangulation - with the possible addition of
        some edges that were a point's only connection to the rest of the triangulation, found
        in very flat or narrow sets of points

        triangles: key: Triangle.get_key(), value: Triangle. Dictionary containing the
        triangulation. If self.ready, is empty or contains the final triangulation without super
        connected triangles

        triangles_with_edge: Dictionary containing keys of Triangles in self.triangles that share
            the Edge
            key: edge key
            value: triangle object

        ready: when False, triangulation is ongoing
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
        self.rejected_points = set()
        self.next_points = deque()
        self.point_pushed_back = False
        self.point_tries = {}
        self.super_verts = None
        self.super_tri_key = None
        self.super_storage = []
        self.edges = {}
        self.bounding_edges = set()
        self.final_edges = set()
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
        if config.any_debug:
            print(f"-----------\nadding points:\n{points}\n------------")
        if points and self.ready:
            new_points = list(set(points) - set(self.points))
            self.next_points.extend(new_points)
            self.points += new_points
            self.create_super_tri()
            self.ready = False

    def triangulate_point(self, point):
        """Single point triangulation. Simply iterates through existing triangles to find if their
        circumcircle encompasses the given point. Bad triangles are removed and the edges around
        their connected area are used to form new triangles with the new point.
        
        Parameters:
            point: tuple of x,y coordinates expected to lie within the boudaries
        """
        self.point_pushed_back = False
        if point not in self.point_tries:
            self.point_tries[point] = 0
        elif self.point_tries[point] > len(self.rejected_points) + 1:
            self.reject_point(point)
            return
        new_vertex = Vertex(point[0],point[1])
        if config.bw_debug:
            print("triangulating", new_vertex)
        bad_triangles = set()
        self.visualize_new(new_vertex, active=True, reset_active=True)
        for triangle in self.triangles.values():
            try:
                new_vertex_in_circumcircle = triangle.vertex_in_circumcircle(new_vertex)
            except ValueError:
                self.handle_vertex_in_circumcircle_value_error(new_vertex.get_coord())
                return
            triangle.visualize_circle(self.visualizer_queue,
                                      vertex_inside=new_vertex_in_circumcircle)
            if new_vertex_in_circumcircle:
                self.handle_found_triangle(triangle, bad_triangles, new_vertex)
                if self.point_pushed_back:
                    return
                else:
                    break
        bad_tri_edgecount = {}
        for triangle in bad_triangles:
            for edge in triangle.get_edges():
                key = edge.get_key()
                if not key in bad_tri_edgecount:
                    bad_tri_edgecount[key] = 0
                bad_tri_edgecount[key] += 1
                # self.visualize_new(edge, active=True, reset_active=True)
        polygon = [self.edges[key] for key, count in bad_tri_edgecount.items() if count == 1]
        # for edge in polygon:
            # self.visualize_new(edge, active=True)
        for triangle in bad_triangles:
            self.remove_triangle(triangle)
        for edge in polygon:
            vertex_a, vertex_b = edge.get_vertices()
            if config.bw_debug:
                print("validating triangle: new vert with edge:",edge)
            if self.is_valid_triangle(vertex_a, vertex_b, new_vertex):
                self.add_triangle(vertex_a, vertex_b, new_vertex)

    def handle_found_triangle(self, triangle, bad_triangles, new_vertex):
        if self.point_pushed_back:
            # triangle.visualize_remove_circle(self.visualizer_queue)
            return
        for vertex in triangle.get_vertices():
            self.visualize_activate(vertex)
        bad_triangles.add(triangle)
        for edge in triangle.get_edges():
            if not edge.get_key() in self.edges:
                self.edges[edge.get_key()] = edge
            # self.visualize_new(edge, active=True, reset_active=True)
            self.visualize_activate(triangle)
        # triangle.visualize_remove_circle(self.visualizer_queue)
        for edge in triangle.get_edges():
            for triangle_by_edge in self.triangles_with_edge[edge.get_key()]:
                try:
                    new_vertex_in_circumcircle = triangle_by_edge.vertex_in_circumcircle(new_vertex)
                except ValueError:
                    self.handle_vertex_in_circumcircle_value_error(new_vertex.get_coord())
                    return
                if triangle_by_edge not in bad_triangles \
                        and new_vertex_in_circumcircle:
                    bad_triangles.add(triangle_by_edge)
                    self.handle_found_triangle(triangle_by_edge, bad_triangles, new_vertex)

    def handle_vertex_in_circumcircle_value_error(self, point):
        """point has been found within error margin of a circumcircle, push it to the back of the
        deque to try triangulate it later"""
        self.point_pushed_back = True
        self.next_points.append(point)
        self.point_tries[point] += 1
        if config.problematic_point_debug:
            print(f"{point}: Potentially problematic point location, pushing to back of" \
                f" deque. Tries: {self.point_tries[point]}")

    def iterate_once(self):
        while self.next_points:
            point = self.next_points.popleft()
            self.triangulate_point(point)
            break
        if not self.next_points:
            self.finalize_triangulation()
            self.ready = True

    def triangulate_all(self):
        while self.next_points:
            point = self.next_points.popleft()
            self.triangulate_point(point)
        self.finalize_triangulation()
        self.ready = True

    def create_super_tri(self):
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
            self.restore_super_triangle()

    def get_super_vertices(self):
        xs, ys = zip(*self.points)
        min_x, min_y, max_x, max_y = min(xs), min(ys), max(xs), max(ys)
        min_any, max_any = min(min_x, min_y), max(max_x, max_y)
        vertex_a = Vertex(min_any - max_any * 10, min_any - max_any * 10)
        vertex_b = Vertex(min_any - max_any * 10, max_any * 20)
        vertex_c = Vertex(max_any * 20, min_any - max_any * 10)
        return (vertex_a, vertex_b, vertex_c)

    def finalize_triangulation(self):
        self.remove_super_tri()
        if self.visualizer_queue:
            self.visualizer_queue.put(methodcaller("clear_entities_by_type", circumcircles=True))
            self.draw_final_circumcircles()
            for triangle in self.triangles:
                self.visualize_remove(triangle)
        self.find_final_edges()

    def remove_super_tri(self):
        for triangle in list(self.triangles.values()):
            for super_vertex in self.super_verts:
                if super_vertex in triangle.get_vertices():
                    for edge in triangle.get_edges():
                        if not edge.get_vertices()[0] in self.super_verts and \
                           not edge.get_vertices()[1] in self.super_verts:
                            if edge in self.bounding_edges:
                                # While removing the super-connected triangles we seem to be
                                # removing both edges from between two triangulated points.
                                # For our purposes it's probably best to keep it.
                                self.final_edges.add(edge)
                            self.bounding_edges.add(edge)
                    self.super_storage.append(triangle)
                    self.remove_triangle(triangle)

    def restore_super_triangle(self):
        if config.bw_debug:
            print("RESTORING SUPER STORAGE:", self.super_storage)
        for triangle in self.super_storage:
            self.triangles[triangle.get_key()] = triangle
            for edge in triangle.get_edges():
                key = edge.get_key()
                if key not in self.triangles_with_edge:
                    self.triangles_with_edge[key] = []
                self.triangles_with_edge[key].append(triangle)
            self.visualize_new(triangle)
        self.super_storage = []

    def find_final_edges(self):
        for triangle in self.triangles.values():
            for edge in triangle.get_edges():
                self.final_edges.add(edge)

    def draw_final_circumcircles(self):
        if config.draw_final_circumcircles:
            for triangle in self.triangles.values():
                triangle.visualize_circle(self.visualizer_queue,
                                          color=config.color_circumcircle_final)

    def add_triangle(self, vertex_a, vertex_b, vertex_c):
        triangle = Triangle(vertex_a, vertex_b, vertex_c, self.edges)
        self.triangles[triangle.get_key()] = triangle
        edges = (Edge(vertex_a, vertex_b),
                 Edge(vertex_a, vertex_c),
                 Edge(vertex_b, vertex_c)
                )
        for edge in edges:
            key = edge.get_key()
            if key not in self.edges:
                self.edges[key] = edge
            if key not in self.triangles_with_edge:
                self.triangles_with_edge[key] = []
            self.triangles_with_edge[key].append(triangle)

        self.visualize_new(triangle)
        return triangle.get_key()

    def remove_triangle(self, triangle):
        if not triangle.get_key() in self.triangles:
            if config.bw_debug:
                print(f"remove triangle: NOT FOUND {triangle}")
            return triangle
        if config.bw_debug:
            for vert in self.super_verts:
                if vert not in triangle.get_vertices():
                    print(f"remove triangle: {triangle}")
        self.triangles.pop(triangle.get_key())
        edges = triangle.get_edges()
        for edge in edges:
            key = edge.get_key()
            self.edges[key] = edge
            self.triangles_with_edge[key].remove(triangle)
            # if self.triangles_with_edge[key] == []:
            #     try:
            #         self.visualize_remove(edge)
            #     except KeyError:
            #         if config.visualizer_debug:
            #             print("bw.KeyError:",edge)
        self.visualize_remove(triangle)

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
                self.visualizer_queue.put(methodcaller("new_vertex",
                                                       bw_object, active, reset_active))
            elif isinstance(bw_object, Edge):
                self.visualizer_queue.put(methodcaller("new_edge",
                                                       bw_object, active, reset_active))
            elif isinstance(bw_object, Triangle):
                self.visualizer_queue.put(methodcaller("new_triangle",
                                                       bw_object, active, reset_active))

    def visualize_activate(self, bw_object, reset_active=False):
        if self.visualizer_queue:
            if isinstance(bw_object, Vertex):
                self.visualizer_queue.put(methodcaller("activate_vertex",
                                                       bw_object, reset_active))
            elif isinstance(bw_object, Edge):
                self.visualizer_queue.put(methodcaller("activate_edge",
                                                       bw_object, reset_active))
            elif isinstance(bw_object, Triangle):
                self.visualizer_queue.put(methodcaller("activate_triangle",
                                                       bw_object, reset_active))

    def is_valid_triangle(self, vertex_a, vertex_b, vertex_c):
        two_or_more_same_points = vertex_a == vertex_b \
                               or vertex_b == vertex_c \
                               or vertex_a == vertex_c
        edge_a, edge_b = Edge(vertex_a, vertex_b), Edge(vertex_b, vertex_c)
        slope_a, slope_b = edge_a.get_slope(), edge_b.get_slope()
        if two_or_more_same_points or slope_a == slope_b:
            if config.any_debug:
                print("====================================\n",
                      "invalid triangle: ", vertex_a, vertex_b, vertex_c,
                  f"\n  slopes {slope_a}, {slope_b}",
                  "=======================")
            return False
        return True

    def reject_point(self, point):
        print(f"REJECTED {point}")
        self.rejected_points.add(point)
        self.visualize_remove(Vertex(point[0], point[1]))


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
        return sqrt(self.distance_from_squared(vertex))

    def distance_from_squared(self, vertex):
        return (self.x - vertex.x)**2 + (self.y - vertex.y)**2

class Edge:
    def __init__(self, vertex_a:Vertex, vertex_b:Vertex):
        self.vertex_a, self.vertex_b = sorted((vertex_a, vertex_b))
        self.midpoint = None
        self.slope = None
        self.pb_slope = None
        self.pb_intercept = None
        self.length = None

    def __repr__(self):
        return f"Edge{self.get_key()}"

    def __eq__(self, edge:"Edge"):
        return (self.vertex_a == edge.vertex_a and self.vertex_b == edge.vertex_b)

    def __hash__(self):
        return hash(self.get_key())

    def get_key(self):
        return self.get_coords()

    def get_coords(self):
        return (self.vertex_a.get_coord(), self.vertex_b.get_coord())

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
        self.circumcircle_radius_squared = None

    def __repr__(self):
        return  f"Triangle{self.vertex_a.get_coord()}" \
                        f"{self.vertex_b.get_coord()}" \
                        f"{self.vertex_c.get_coord()}"

    def get_vertices(self):
        return (self.vertex_a, self.vertex_b, self.vertex_c)

    def get_coords(self):
        return [vertex.get_coord() for vertex in self.get_vertices()]

    def get_key(self):
        return tuple(sorted((self.vertex_a, self.vertex_b, self.vertex_c)))

    def get_edges(self):
        return (self.edge_lookup[tuple(sorted((self.vertex_a.get_coord(),
                                               self.vertex_b.get_coord())))],
                self.edge_lookup[tuple(sorted((self.vertex_a.get_coord(),
                                               self.vertex_c.get_coord())))],
                self.edge_lookup[tuple(sorted((self.vertex_b.get_coord(),
                                               self.vertex_c.get_coord())))]
            )

    def get_circumcircle_radius_squared(self):
        if not self.circumcircle_radius_squared:
            a, b, c = [edge.get_length() for edge in self.get_edges()]
            self.circumcircle_radius_squared = (a*b*c)**2 / ((a+b+c)*(b+c-a)*(c+a-b)*(a+b-c))
        return self.circumcircle_radius_squared

    def get_circumcircle_radius(self):
        if not self.circumcircle_radius:
            self.circumcircle_radius = sqrt(self.get_circumcircle_radius_squared())
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
                if config.bw_debug:
                    print("HELP!!!!!!!!!!!! BR", self)
                    # fails when points are in a straight line
                    # but this is checked for with BowyerWatson.is_valid_triangle()
            x = (c_2 - c_1) / det
            y = ((a_1 * c_2) - (a_2 * c_1)) / det
            self.circumcenter = Vertex(x,y)
        return self.circumcenter

    def vertex_in_circumcircle(self, vertex):
        dist = self.get_circumcenter().distance_from_squared(vertex)
        r = self.get_circumcircle_radius_squared()
        if isclose(dist, r):
            raise ValueError("Potentially problematic point location")
        elif dist <= r:
            return True
        return False

    def select_edges_for_circumcenter_f(self):
        """Edges with perpendicular bisectors on lines of form y = 0x + c will be omitted"""
        edges = self.get_edges()
        valid_edges = []
        for edge in edges:
            if edge.get_pb_slope() == float("inf") or edge.get_pb_slope() == float("-inf"):
                continue
            valid_edges.append(edge)
        return valid_edges

    def visualize_circle(self, visualizer_queue, vertex_inside=False, color=None):
        if visualizer_queue is not None:
            visualizer_queue.put(methodcaller("new_circle", self, vertex_inside, color))

    def visualize_remove_circle(self, visualizer_queue):
        if visualizer_queue is not None:
            visualizer_queue.put(methodcaller("remove_circle", self))

    def get_circumcircle_key(self):
        return "VCCir" + str(self)
