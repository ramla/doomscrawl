import heapq
from operator import methodcaller
from math import sqrt
import pygame
import config
from bowyer_watson import Vertex

class AStar:
    def __init__(self, dungeon_mask, room_lookup, visualizer_queue=None):
        self.room_lookup = room_lookup
        self.visualizer_queue = visualizer_queue
        print("viz queue",self.visualizer_queue)
        space_size_px = (config.thickness*1.5, config.thickness*1.5)
        self.space = pygame.Mask(space_size_px, fill=True)
        self.dungeon_mask = dungeon_mask
        self.goal, self.goal_mask = None, None
        self.goal_mask_cumulative = pygame.Mask((config.viewport_x, config.viewport_y))

    def get_path(self, a, b, slope):
        start = self.centerify(self.room_lookup[a].get_door(slope))
        if self.visualizer_queue:
            self.visualizer_queue.put(methodcaller("new_vertex", Vertex(start[0], start[1]),
                                                    active=True, reset_active=True))
        self.goal = self.centerify(self.room_lookup[b].get_door(slope, b_room=True))
        if self.visualizer_queue:
            self.visualizer_queue.put(methodcaller("new_vertex", Vertex(self.goal[0], self.goal[1]),
                                                    active=True, reset_active=False))
        self.goal_mask = pygame.Mask((config.viewport_x, config.viewport_y))
        self.goal_mask.draw(self.space, self.goal)
        self.goal_mask_cumulative.draw(self.space, self.goal)

        path = set()
        prev_pos_in_path = False
        queue = [(self.euclidean(a, b), start)]
        heapq.heapify(queue)
        while len(queue) > 0:
            _, pos = heapq.heappop(queue)
            # if self.visualizer_queue:
            #     self.visualizer_queue.put(methodcaller("new_vertex", Vertex(pos[0], pos[1]),
            #                                            active=False, reset_active=False))
            if self.goal_reached(pos):
                self.goal_mask_cumulative.draw(self.space, pos)
                return path, self.goal_mask_cumulative
            if pos in path and prev_pos_in_path:
                path.remove(pos)
            elif pos in path:
                prev_pos_in_path = True
            else:
                prev_pos_in_path = False
                path.add(pos)
                self.goal_mask_cumulative.draw(self.space, pos)
            for neighbor in self.neighbors(pos):
                distance = self.euclidean(neighbor, self.goal)
                heapq.heappush(queue, (distance, neighbor))
        return path, self.goal_mask_cumulative

    def neighbors(self, pos):
        step = config.corridor_width/2
        neighbors = ((pos[0]+step, pos[1]),
                     (pos[0]-step, pos[1]),
                     (pos[0], pos[1]+step),
                     (pos[0], pos[1]-step))
        neibs = [new_pos for new_pos in neighbors if self.is_valid_position(new_pos)]
        return neibs

    def euclidean(self, a, b):
        return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    def is_valid_position(self, pos):
        overlap, reached = self.dungeon_mask.overlap(self.space, pos), self.goal_reached(pos)
        return not overlap or reached

    def goal_reached(self, pos):
        reached = self.goal_mask.overlap(self.space, pos)
        return reached

    def draw_collision_overlay(self, viewport):
        overlay = self.goal_mask_cumulative.to_surface(setcolor=(200, 0, 0, 100),
                                                       unsetcolor=(0, 0, 0, 0))
        viewport.blit(overlay, (0,0))

    def centerify(self, point):
        return point[0]-config.thickness*.75, point[1]-config.thickness*.75
