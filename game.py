import pygame
from pygame.locals import *
import sys
from random import randint

from dungeon import Dungeon
from player import Player
import config


class Doomcrawl:
    def __init__(self):
        pygame.init()
        self.viewport = pygame.display.set_mode((config.viewport_x,config.viewport_y), pygame.RESIZABLE)
        pygame.display.set_caption('Doomscrawl')

        self.dungeon = Dungeon((config.viewport_x, config.viewport_y))
        self.player = Player(self.dungeon.player_start_pos, (config.thickness, config.thickness))

    def start(self):
        self.loop(config.target_fps)
        sys.exit()

    def loop(self, target_fps):
        FPS = pygame.time.Clock()
        self.running = True
        while self.running:
            frame_time = FPS.tick(target_fps) / 1000

            self.process_events()
            self.process_key_input()

            self.player.clamp_ip(self.viewport.get_rect())

            self.viewport.fill(config.color["bg"])

            for room in self.dungeon.rooms:
                room.anim_pop_tick(self.viewport, frame_time)
                pygame.draw.rect(self.viewport, config.color["col1"], room)

            pygame.draw.rect(self.viewport, config.color["hilite1"], self.player)

            if config.collision_debug:
                self.dungeon.draw_collision_overlay(self.viewport)
                self.player.draw_collision_overlay(self.viewport)

            pygame.display.flip()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == KEYDOWN:
                if event.key == pygame.K_r:
                    self.dungeon.add_room()
            if event.type == KEYDOWN:
                if event.key == pygame.K_t:
                    self.bw = BowyerWatson(self.dungeon.get_room_centers())


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

