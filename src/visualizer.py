import queue
from operator import methodcaller
import pygame
import pygame.freetype
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
        if config.draw_coords:
            self.font = pygame.freetype.Font(config.FONTFILE, config.thickness * 1)

    def visualize(self, frame_time):
        self.accumulator -= frame_time
        while self.accumulator <= 0:
            try:
                event = self.event_queue.get_nowait()
                event(self)
                self.accumulator = self.delay_min
            except queue.Empty:
                break
        to_delete = []
        for entity in self.entities.values():
            entity.draw(self.viewport, frame_time)
            if isinstance(entity, VisualCircumcircle):
                if entity.delete_me and entity.accumulator <= 0:
                    to_delete.append(entity)
            elif isinstance(entity, VisualVertex) and config.draw_coords:
                text_surface = self.create_text_surface(str(entity.center))
                self.viewport.blit(text_surface, entity.center)
        for entity in to_delete:
            self.entities.pop(entity.keystring)

    def process_all(self):
        while not self.event_queue.empty():
            event = self.event_queue.get_nowait()
            event(self)
            self.accumulator = 0

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

    def new_circle(self, triangle, color=None):
        """Add the circumcircle of the triangle to entities to draw"""
        circle = VisualCircumcircle(triangle, color=color)
        triangle.circumcircle_key = f"{circle}"
        self.entities[circle.get_key()] = circle

    def remove_vertex(self, vertex):
        if config.visualizer_debug:
            print("removing vertex", vertex)
        try:
            self.entities.pop(vertex)
        except KeyError:
            if config.visualizer_debug:
                print("visualizer.remove_vertex() KeyError:", vertex)

    def remove_edge(self, edge):
        if config.visualizer_debug:
            print("removing edge", edge.get_key())
        try:
            self.entities.pop(edge.get_key())
        except KeyError:
            if config.visualizer_debug:
                print("visualizer.remove_triangle() KeyError:", edge)

    def remove_triangle(self, triangle):
        if config.visualizer_debug:
            print("removing tri", triangle)
        try:
            self.entities.pop(triangle)
        except KeyError:
            if config.visualizer_debug:
                print("visualizer.remove_triangle() KeyError:", triangle)

    def remove_circle(self, triangle):
        if config.visualizer_debug:
            print("entities:",self.entities)
        try:
            self.entities[triangle.get_circumcircle_key()].anim_drop()
            if config.visualizer_debug:
                print("circle drop animation initiated")
        except KeyError:
            if config.visualizer_debug:
                print("visualizer.remove_circle() KeyError:", triangle.circumcircle_key,
                      "for", triangle)

    def activate_vertex(self, vertex, reset_active):
        if reset_active:
            for entity in self.entities:
                if isinstance(entity, VisualVertex):
                    entity.deactivate()
                    if config.visualizer_debug:
                        print("deactivating vertex",vertex)
        try:
            self.entities[vertex].activate()
        except KeyError:
            if config.visualizer_debug:
                print("visualizer.activate_vertex() KeyError:", vertex)

    def activate_triangle(self, triangle, reset_active):
        if reset_active:
            for entity in self.entities:
                if isinstance(entity, VisualTriangle):
                    entity.deactivate()
                    if config.visualizer_debug:
                        print("deactivating triangle",triangle)
        try:
            self.entities[triangle.get_key()].activate()
        except KeyError:
            if config.visualizer_debug:
                print("visualizer.activate_triangle() KeyError:", triangle)

    def animate_entity(self, key, anim_func, next_event_delay=None):
        if next_event_delay is None or not config.delay_visualisation:
            next_event_delay = self.delay_min
        self.accumulator = next_event_delay
        anim_func(self.entities[key])

    def create_text_surface(self, text):
        text_surface = pygame.Surface((config.viewport_x, config.viewport_y), pygame.SRCALPHA)
        line_height = self.font.get_sized_height()
        x, y = config.thickness * 4, config.thickness * 3
        for line in text.splitlines():
            self.font.render_to(text_surface, (x, y),
                                line, config.color["light1"])
            y += line_height
        return text_surface

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

    def anim_new(self, duration=config.vertex_anim_duration, scale=config.vertex_anim_new_scale):
        self.accumulator = duration
        self.radius = scale*self.base_radius
        self.radius_rate = (self.radius - self.base_radius) / (duration * config.target_fps)

    def activate(self):
        self.active = True
        self.color = self.color_active
        self.anim_new(scale=2*config.vertex_anim_new_scale)

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
        self.bw_id = id(edge)
        self.bw_key = edge.get_key()

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

    def get_bw_id(self):
        return self.bw_id

    def get_bw_key(self):
        return self.bw_key


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
        self.bw_id = id(triangle)
        self.bw_key = triangle.get_key()

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

    def get_bw_id(self):
        return self.bw_id

    def get_bw_key(self):
        return self.bw_key


class VisualCircumcircle:
    def __init__(self, triangle, width=2, color=None):
        self.accumulator = 0
        self.delete_me = False
        self.keystring = "VCCir" + str(triangle)
        self.width = width
        if color is None:
            color = config.color_circumcircle
        self.color_normal = color
        self.color = pygame.Color(self.color_normal)
        self.color_fill = pygame.Color(config.color_circumcircle_fill)
        self.radius = triangle.circumcircle_radius
        self.center = triangle.circumcenter.get_coord()
        self.alpha_surface = None
        self.draw_surface()

    def draw_surface(self):
        self.blit_dest = (self.center[0] - self.radius, self.center[1] - self.radius)
        self.alpha_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.alpha_surface, self.color_fill,
                           (self.radius, self.radius), self.radius, 0)
        pygame.draw.circle(self.alpha_surface, self.color,
                           (self.radius, self.radius), self.radius, int(self.width))

    def draw(self, viewport, frame_time):
        if self.accumulator > 0:
            # self.radius *= config.circumcircle_anim_drop_scale
            self.accumulator -= frame_time
            self.color.a = int(config.circumcircle_anim_drop_scale * self.color.a)
            self.color_fill.a = int(config.circumcircle_anim_drop_scale * self.color_fill.a)
            self.draw_surface()
        viewport.blit(self.alpha_surface, self.blit_dest)

    def anim_drop(self, duration=config.circumcircle_anim_duration):
        self.accumulator = duration
        self.delete_me = True

    def get_key(self):
        return self.keystring
