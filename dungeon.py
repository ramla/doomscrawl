import pygame
from random import randint
import config

class Dungeon:
    def __init__(self, screen_size):
        self.rooms = []
        self.screen_size = screen_size
        self.init_collision_surface()
        self.render_collision_mask()
        self.init_texture()
        self.add_room(fail_allowed=False)
        self.player_start_pos = self.rooms[0].center

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
        if fail_allowed:
            tries = 10
        else:
            tries = 99999

        while tries > 0:
            room = Room(size=size, pos=pos, center=center)
            if config.room_debug:
                print(f"center {center}, size {room.size}, offset {room.offset}")
            if not self.collision_mask.overlap(room.mask, room.get_mask_offset()):
                self.collision_surface.blit(room.surface, room.offset)
                self.render_collision_mask()
                room.anim_pop_init()
                self.rooms.append(room)
            tries -= 1
        if config.room_debug:
            print(f"room creation failed, tries = {tries}")

    def overlapping_existing(self, mask, offset):
        if self.collision_mask.overlap(mask, offset):
            return True
        return False

    def get_room_centers(self):
        centers = []
        for room in self.rooms:
            centers.append(room.center)
        return centers


class Room(pygame.Rect):
    def __init__(self, size=None, pos=None, center=None):
        if size == None:
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

        margin = config.thickness
        self.mask = pygame.Mask((self.size[0]+2*margin, self.size[1]+2*margin), fill=True)

        self.surface = pygame.Surface(self.size)
        self.surface.fill(config.color["col1"])

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

    def get_mask_offset(self):
        x = self.offset[0] - config.thickness
        y = self.offset[1] - config.thickness
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

