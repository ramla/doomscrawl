import pygame


class Player(pygame.Rect):
    def __init__(self, starting_pos:tuple, size:tuple, speed=5):
        super().__init__(starting_pos[0], starting_pos[1], size[0], size[1])
        self.speed = speed
        self.size = size
        self.collision_mask = pygame.Mask((size[0], size[1]), fill=True)

    def draw_collision_overlay(self, viewport):
        overlay = self.collision_mask.to_surface(setcolor=(200, 0, 0, 100), unsetcolor=(0, 0, 0, 0))
        viewport.blit(overlay, (self.x, self.y))
