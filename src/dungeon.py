from random import randint
import pygame
import config
from astar import AStar

class Dungeon:
    def __init__(self, screen_size, rooms, exceptions=False, visualizer_queue=None):
        self.screen_size = screen_size
        self.init_collision_surface()
        self.render_collision_mask()
        self.init_texture()
        self.ignore_collision = exceptions
        self.rooms = {}
        self.rejected_rooms = set()
        self.corridors = {}
        if rooms is None:
            self.add_room(fail_allowed=False)
            self.player_start_pos = list(self.rooms.values())[0].get_center()
        else:
            self.player_start_pos = rooms[0][0]
            for room in rooms:
                self.add_room(center=room[0], size=room[1])
        self.astar = AStar(self.rooms, visualizer_queue=visualizer_queue)

    def init_collision_surface(self):
        self.collision_surface = pygame.Surface((self.screen_size[0], self.screen_size[1]))
        self.collision_surface.fill((255,255,255))
        actual = pygame.Surface((self.screen_size[0]-20, self.screen_size[1]-20))
        actual.fill((0,0,0))
        self.collision_surface.blit(actual,(10,10))
        self.collision_surface.set_colorkey((0,0,0))

    def init_texture(self):
        self.texture = pygame.Surface((self.screen_size[0], self.screen_size[1]))
        self.texture.fill((0,0,0,0))

    def render_collision_mask(self):
        self.collision_mask = pygame.mask.from_surface(self.collision_surface)

    def draw_collision_overlay(self, viewport):
        overlay = self.collision_mask.to_surface(setcolor=(0, 200, 0, 100),
                                                 unsetcolor=(0, 0, 0, 0))
        viewport.blit(overlay, (0, 0))

    def add_room(self, size=None, pos=None, center=None, fail_allowed=True):
        if center is not None:
            tries = 1
        elif fail_allowed:
            tries = 30
        else:
            tries = 9999

        while tries > 0:
            room = Room(size=size, pos=pos, center=center)
            if config.room_debug:
                print(f"center {center}, size {room.size}, offset {room.offset}")
            if (not self.collision_mask.overlap(room.mask,
                                                room.get_mask_offset(config.room_margin))
                or self.ignore_collision
            ):
                self.collision_surface.blit(room.surface, room.offset)
                self.render_collision_mask()
                room.anim_pop_init()
                self.rooms[room.get_center()] = room
                return
            tries -= 1
        if config.room_debug or center is not None:
            print(f"Room creation failed (overlapping with existing): center {center}")
            self.rejected_rooms.add(center)

    def get_room_centers(self):
        centers = []
        sizes = []
        for room in self.rooms.values():
            centers.append(room.get_center())
        if config.room_debug:
            for room in self.rooms.values():
                sizes.append(room.size)
            print("room list:",list(zip(centers, sizes)))
        return centers

    def handle_point_rejection(self, point):
        for room in self.rooms.values():
            if room.get_center() == point:
                self.rooms.pop(room.get_center())
                break

    def create_corridors(self, edges):
        for edge in edges:
            key = edge.get_key()
            self.corridors[key] = Corridor(edge, self.astar)
        for corridor in self.corridors.values():
            self.collision_mask.draw(corridor.get_mask(), (0,0))

    def get_player_room_center(self):
        return self.player_start_pos

    def draw_dungeon(self, viewport, frame_time):
        for room in self.rooms.values():
            room.anim_pop_tick(viewport, frame_time)
            pygame.draw.rect(viewport, config.color_room, room)
        for corridor in self.corridors.values():
            if corridor.bitmap is None:
                corridor.create_bitmap()
            viewport.blit(corridor.bitmap, (0, 0))


class Room(pygame.Rect):
    def __init__(self, size=None, pos=None, center=None):
        if size is None:
            self.size = self.get_random_size()
        else:
            self.size = size

        if pos:
            self.offset = pos
        elif center:
            self.offset = (center[0] - self.size[0] // 2, center[1] - self.size[1] // 2)
        else:
            self.offset = self.get_random_pos()

        super().__init__(self.offset[0], self.offset[1], self.size[0], self.size[1])

        self.ratio = self.width / self.height
        self.pop_timer = 0
        self.animation_copy = None

        self.mask = self.get_mask_with_margin(config.room_margin)

        self.surface = pygame.Surface(self.size)
        self.surface.fill(config.color["col1"])

    def get_mask_with_margin(self, margin):
        return pygame.Mask((self.size[0]+2*margin,
                           self.size[1]+2*margin),
                           fill=True)

    def get_center(self):
        return self.center

    def get_door(self, slope, b_room=False):
        doors = self.get_doors()
        delta = 1
        if (slope > 1 and b_room) or (slope < -1 and not b_room):
            # door on bottom edge
            return doors[0], (0,delta)
        if slope > 1 or (slope < -1 and b_room):
            # door on top edge
            return doors[1], (0,-delta)
        if b_room:
            # door on left edge
            return doors[2], (-delta,0)
        # door on right edge
        return doors[3], (delta,0)

    def get_doors(self):
        return (self.center[0], self.center[1]-self.size[1]/3), \
               (self.center[0], self.center[1]+self.size[1]/3), \
               (self.center[0]-self.size[0]/3, self.center[1]), \
               (self.center[0]+self.size[0]/3, self.center[1])

    def get_random_size(self):
        x = randint(config.room_size_min[0], config.room_size_max[0])
        y = randint(config.room_size_min[1], config.room_size_max[1])
        return (x,y)

    def get_random_center(self):
        x = randint(config.thickness + self.size[0] // 2,
                    config.viewport_x - config.thickness - self.size[0] // 2)
        y = randint(config.thickness + self.size[1] // 2,
                    config.viewport_y - config.thickness - self.size[1] // 2)
        return (x,y)

    def get_random_pos(self):
        x = randint(config.thickness, config.viewport_x - config.thickness - self.size[0])
        y = randint(config.thickness, config.viewport_y - config.thickness - self.size[1])
        return (x,y)

    def get_mask_offset(self, margin):
        x = self.offset[0] - margin
        y = self.offset[1] - margin
        return (x,y)

    def anim_pop_init(self):
        self.pop_timer = 2
        self.animation_copy = self.inflate(2* config.thickness, 2* config.thickness)

    def anim_pop_tick(self, viewport, frame_time):
        if self.pop_timer > 0:
            self.pop_timer -= frame_time
            self.animation_copy.center = self.center
            self.animation_copy.width -= (frame_time * config.thickness * 4)
            self.animation_copy.height -= (frame_time * config.thickness * 4)
            pygame.draw.rect(viewport, config.color["col1"], self.animation_copy)
        else:
            pass


class Corridor:
    def __init__(self, edge, astar):
        self.edge = edge
        self.a, self.b = self.edge.get_coords()
        self.bitmap = None

        slope = edge.get_slope()
        self.path = astar.get_path(self.a, self.b, slope)
        self.mask = pygame.Mask((config.viewport_x, config.viewport_y))
        corridor_space = pygame.Mask((config.corridor_width, config.corridor_width), fill=True)
        for pos in self.path:
            self.mask.draw(corridor_space, pos)

    def get_mask(self):
        return self.mask

    def create_bitmap(self):
        self.bitmap = self.get_mask().to_surface(setcolor=config.color_room,
                                                unsetcolor=(0, 0, 0, 0))
