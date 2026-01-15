import pygame
from random import randint
import config

class Dungeon:
    def __init__(self, screen_size, player_startpos):
        self.screen_size = screen_size
        self.init_collision_surface()
        self.render_collision_mask()
        self.init_texture()

    def init_collision_surface(self):
        self.collision_surface = pygame.Surface((self.screen_size[0], self.screen_size[1]))
        self.collision_surface.fill((0,0,0))
        self.collision_surface.set_colorkey((0,0,0))

    def init_texture(self):
        self.texture = pygame.Surface((self.screen_size[0], self.screen_size[1]))
        self.texture.fill((0,0,0,0))

    def render_collision_mask(self):
        self.collision_mask = pygame.mask.from_surface(self.collision_surface)

    def draw_collision_overlay(self, viewport):
        overlay = self.collision_mask.to_surface(setcolor=(0, 200, 0, 100), unsetcolor=(0, 0, 0, 0))
        viewport.blit(overlay, (0, 0))

    def add_room(self, size=None, pos=None, center=None):
        if size == None:
            size = self.randomize_room_size()

        room = pygame.Surface(size)
        room.fill(config.color["col1"])

        offset = (0,0)
        if pos:
            offset = pos
        elif center:
            offset = (center[0] - size[0]//2, center[1] - size[1]//2)
        
        self.collision_surface.blit(room, offset)
        self.render_collision_mask()
        self.texture.blit(room, offset)

    def randomize_room_size(self):
        x = randint(config.room_size_min[0], config.room_size_max[0])
        y = randint(config.room_size_min[1], config.room_size_max[1])
        return (x,y)
