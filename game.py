import pygame
from pygame.locals import *
import sys
from dungeon import Dungeon
from player import Player
import config


class Doomcrawl:
    def __init__(self):
        pygame.init()
        player_startpos = ((config.viewport_x - config.thickness // 2) // 2, config.viewport_y - config.thickness)

        self.viewport = pygame.display.set_mode((config.viewport_x,config.viewport_y), pygame.RESIZABLE)
        pygame.display.set_caption('Doomscrawl')
        
        self.player = Player(player_startpos, (config.thickness, config.thickness))
        self.dungeon = Dungeon((config.viewport_x, config.viewport_y), player_startpos)
        self.dungeon.add_room(config.start_room_size, center=player_startpos)

    def start(self):
        self.loop()
        sys.exit()

    def loop(self):
        FPS = pygame.time.Clock()
        self.running = True
        while self.running:
            self.process_events()
            self.process_key_input()

            self.player.clamp_ip(self.viewport.get_rect())

            self.viewport.fill(config.color["bg"])

            pygame.draw.rect(self.viewport, config.color["hilite1"], self.player)

            if config.collision_debug:
                self.dungeon.draw_collision_overlay(self.viewport)
                self.player.draw_collision_overlay(self.viewport)

            pygame.display.flip()
            FPS.tick(60)
    
    def process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

    def process_key_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.dungeon.collision_mask.overlap(self.player.collision_mask, (self.player.x - self.player.speed - self.player.size[0], self.player.y)):
                self.player.move_ip(-self.player.speed, 0)
            elif config.collision_debug:
                print("colliding left")
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.dungeon.collision_mask.overlap(self.player.collision_mask, (self.player.x + self.player.speed + self.player.size[0], self.player.y)):
                self.player.move_ip(self.player.speed, 0)
            elif config.collision_debug:
                print("colliding right")
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.dungeon.collision_mask.overlap(self.player.collision_mask, (self.player.x, self.player.y - self.player.speed - self.player.size[1])):
                self.player.move_ip(0, -self.player.speed)
            elif config.collision_debug:
                print("colliding up")
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if self.dungeon.collision_mask.overlap(self.player.collision_mask, (self.player.x, self.player.y + self.player.speed + self.player.size[1])):
                self.player.move_ip(0, self.player.speed)
            elif config.collision_debug:
                print("colliding down")

        if keys[pygame.K_q]:
            self.running = False
        # if keys[pygame.K_r]:
        #     self.dungeon.add_room()


