import pygame
import queue
from operator import methodcaller
import config


class Visualizer:
    def __init__(self, viewport):
        self.event_queue = queue.Queue()
        self.viewport = viewport
        self.accumulator = 0
        self.entities = {}
        self.delay_min = config.visualisation_delay_min
        self.active_vertices = []
        self.active_edges = []
        self.active_triangles = []

    def visualize(self, frame_time):
        self.accumulator -= frame_time
        while self.accumulator <= 0:
            try:
                event = self.event_queue.get_nowait()
                event(self)
                self.accumulator = self.delay_min
            except queue.Empty:
                break
        for entity in self.entities.values():
            entity.draw(self.viewport, frame_time)

    def list_entities(self):
        verts, edges, tris = [], [], []
        for entity in self.entities.values():
            if isinstance(entity, VisualVertex):
                verts.append(entity)
            if isinstance(entity, VisualEdge):
                edges.append(entity)
            if isinstance(entity, VisualTriangle):
                tris.append(entity)
        return verts, edges, tris

    def new_vertex(self, vertex, active, reset_active):
        self.entities[vertex] = VisualVertex(center=(vertex.x, vertex.y),
                                                     active=active,
                                                     radius=config.vertex_radius,)
        self.animate_entity(vertex, methodcaller("anim_new"))
        if reset_active:
            for entity in self.active_vertices:
                entity.deactivate()
            self.active_vertices = []
        if active:
            self.active_vertices.append(self.entities[vertex])

    def new_edge(self, edge, active, reset_active):
        self.entities[edge.get_key()] = VisualEdge(edge,
                                                   active=active,
                                                   width=config.edge_width,)
        # self.animate_entity(edge, methodcaller("anim_new"))
        if reset_active:
            for entity in self.active_edges:
                entity.deactivate()
            self.active_edges = []
        if active:
            self.active_edges.append(self.entities[edge.get_key()])


    def new_triangle(self, triangle, active, reset_active):
        self.entities[triangle] = VisualTriangle(triangle,
                                                 active=active,
                                                 width=config.triangle_width,)
        # self.animate_entity(triangle, methodcaller("anim_new"))
        if reset_active:
            for entity in self.active_triangles:
                entity.deactivate()
            self.active_triangles = []
        if active:
            self.active_triangles.append(self.entities[triangle])

        
    def remove_edge(self, edge):
        if config.visualizer_debug:
            print("removing edge",edge.get_key())
        try:
            self.entities.pop(edge.get_key())
        except KeyError:
            if config.visualizer_debug:
                print("visualizer.remove_triangle() KeyError:",edge)

    def remove_triangle(self, triangle):
        if config.visualizer_debug:
            print("removing tri", triangle)
        try:
            self.entities.pop(triangle)
        except KeyError:
            if config.visualizer_debug:
                print("visualizer.remove_triangle() KeyError:",triangle)

    def animate_entity(self, key, anim_func, next_event_delay=None):
        if next_event_delay == None or not config.delay_visualisation:
            next_event_delay = self.delay_min
        self.accumulator = next_event_delay
        anim_func(self.entities[key])


class VisualVertex:
    def __init__(self, center, radius, active, color=config.color_vertex):
        self.center = center
        self.radius = radius
        self.base_radius = radius
        self.radius_rate = 0
        self.color_active = config.color_vertex_active
        self.color_normal = color
        self.accumulator = 0
        if active:
            self.activate()
        else:
            self.deactivate()

    def __repr__(self):
        return f"VVert{self.center}"

    def draw(self, viewport, frame_time):
        if self.accumulator > 0:
            self.radius -= self.radius_rate
            self.accumulator -= frame_time
        else:
            self.radius = self.base_radius
        pygame.draw.circle(viewport, self.color, self.center, self.radius)

    def anim_new(self, duration=config.vertex_anim_duration, scale=config.vertex_anim_pop_scale):
        self.accumulator = duration
        self.radius = scale*self.base_radius
        self.radius_rate = (self.radius - self.base_radius) / (duration * config.target_fps)

    def activate(self):
        self.active = True
        self.color = self.color_active

    def deactivate(self):
        self.active = False
        self.color = self.color_normal


class VisualEdge:
    def __init__(self, edge, width, active, color=config.color_edge):
        self.a = (edge.vertex_a.x, edge.vertex_a.y)
        self.b = (edge.vertex_b.x, edge.vertex_b.y)
        self.width = width
        self.color_normal = color
        self.color_active = config.color_edge_active
        if active:
            self.activate()
        else:
            self.deactivate()
        

    def draw(self, viewport, frame_time):
        pygame.draw.line(viewport, self.color, self.a, self.b, int(self.width))

    def __repr__(self):
        return f"VEdge{self.a}-{self.b}"

    def activate(self):
        self.active = True
        self.color = self.color_active

    def deactivate(self):
        self.active = False
        self.color = self.color_normal


class VisualTriangle:
    def __init__(self, triangle, width, active, color=config.color_tri):
        self.triangle = triangle
        self.width = width
        self.color_normal = color
        self.color_active = config.color_tri_active
        self.points = [(vertex.x, vertex.y) for vertex in triangle.get_vertices()]
        if active:
            self.activate()
        else:
            self.deactivate()
        

    def draw(self, viewport, frame_time):
        pygame.draw.polygon(viewport, self.color, self.points, int(self.width))

    def __repr__(self):
        return f"VTri{self.triangle.get_key()}"
    
    def activate(self):
        self.active = True
        self.color = self.color_active

    def deactivate(self):
        self.active = False
        self.color = self.color_normal