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

    def visualize(self, frame_time):
        self.accumulator -= frame_time
        if self.accumulator <= 0:
            try:
                event = self.event_queue.get_nowait()
                event(self)
                self.accumulator = self.delay_min
            except queue.Empty:
                pass
        for entity in self.entities.values():
            entity.draw(self.viewport, frame_time)

    def new_vertex(self, vertex):
        self.entities[vertex] = VisualVertex(center=(vertex.x, vertex.y),
                                                     radius=config.vertex_radius,
                                                     color=config.color["hilite3"])
        self.animate_entity(vertex, methodcaller("anim_new"))

    def new_edge(self, edge):
        self.entities[edge.get_key()] = VisualEdge(edge,
                                         width=config.edge_width,
                                         color=config.color["light1"])
        # self.animate_entity(edge, methodcaller("anim_new"))

    def new_triangle(self, triangle):
        self.entities[triangle] = VisualTriangle(triangle,
                                                 width=config.triangle_width,
                                                 color=config.color["col2"])
        # self.animate_entity(triangle, methodcaller("anim_new"))
        

    def remove_entity(self, key):
        self.entities.pop(key)

    def animate_entity(self, key, anim_func, next_event_delay=None):
        if next_event_delay == None:
            next_event_delay = self.delay_min
        self.accumulator = next_event_delay
        anim_func(self.entities[key])

class VisualVertex:
    def __init__(self, center, radius, color):
        self.center = center
        self.radius = radius
        self.base_radius = radius
        self.radius_rate = 0
        self.color = color
        self.accumulator = 0

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

class VisualEdge:
    def __init__(self, edge, width, color):
            self.a = (edge.vertex_a.x, edge.vertex_a.y)
            self.b = (edge.vertex_b.x, edge.vertex_b.y)
            self.width = width
            self.color = color

    def draw(self, viewport, frame_time):
        pygame.draw.line(viewport, self.color, self.a, self.b, int(self.width))

class VisualTriangle:
    def __init__(self, triangle, width, color):
        self.triangle = triangle
        self.width = width
        self.color = color
        self.points = [(vertex.x, vertex.y) for vertex in triangle.get_vertices()]

    def draw(self, viewport, frame_time):
        pygame.draw.polygon(viewport, self.color, self.points, int(self.width))
