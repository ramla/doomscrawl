import pygame
from queue import Queue
import config


class Visualizer:
    def __init__(self, viewport):
        self.event_queue = Queue()
        self.viewport = viewport
        self.accumulator = 0
        self.entities = {}

    def visualize(self, frame_time):
        self.accumulator -= frame_time
        if self.accumulator <= 0:
            event = self.event_queue.get_nowait()
            event()
        for entity in self.entities.values():
            entity.draw(self.viewport)

    def new_vertex(self, vertex):
        self.entities[vertex] = VisualVertex(center=(vertex.x, vertex.y),
                                                       radius=config.thickness/3,
                                                       color=config.color["hilite3"])


class VisualVertex:
    def __init__(self, center, radius, color):
        self.center = center
        self.radius = radius
        self.color = color

    def draw(self, viewport):
        pygame.draw.circle(viewport, self.color, self.center, self.radius)