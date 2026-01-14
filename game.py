import pygame
from pygame.locals import *
import sys

class Doomcrawl:
    def __init__(self):
        pygame.init()
        self.screen_x = 800
        self.screen_y = 600
        self.thickness = 15
        self.viewport = pygame.display.set_mode((self.screen_x,self.screen_y), pygame.RESIZABLE)
        pygame.display.set_caption('Doomscrawl')
        self.color = {
            "light1": pygame.Color(235,235,235), # platinum
            "col1": pygame.Color(82,72,156), # dusty grape
            "col2": pygame.Color(64,98,187), # smart blue
            "hilite1": pygame.Color(89,195,195), # strong cyan
            "hilite2": pygame.Color(244,91,105), # bubblegum pink
            "hilite3": pygame.Color(237,240,96), # canary yellow
            "bg": pygame.Color(20,23,30), # ink black
            }
        self.player = pygame.Rect((self.screen_x - self.thickness // 2) // 2, self.screen_y - self.thickness, self.thickness, self.thickness)
        self.playerspeed = 5
        self.collision_mask = pygame.mask.Mask((self.screen_x, self.screen_y))
        self.collision_mask.clear()

    def start(self):
        self.loop()

    def loop(self):
        FPS = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move_ip(-self.playerspeed, 0)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move_ip(self.playerspeed, 0)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.move_ip(0, -self.playerspeed)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player.move_ip(0, self.playerspeed)
            if keys[pygame.K_q]:
                running = False
            self.player.clamp_ip(self.viewport.get_rect())

            self.viewport.fill(self.color["bg"])

            pygame.draw.rect(self.viewport, self.color["hilite1"], self.player)

            pygame.display.flip()
            FPS.tick(60)
        sys.exit()

