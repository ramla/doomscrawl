import heapq
from math import sqrt
import pygame
import config
from operator import methodcaller
from bowyer_watson import Vertex

class AStar:
    def __init__(self, dungeon_mask, room_lookup, visualizer_queue=None):
        self.room_lookup = room_lookup
        self.visualizer_queue = visualizer_queue
        self.space = pygame.Mask((config.corridor_width, config.corridor_width), fill=True)
        self.grid = None
        # self.dungeon_mask = dungeon_mask
        self.rooms_mask = pygame.Mask((config.viewport_x, config.viewport_y))
        self.goals, self.goal_mask = None, None
        self.corridor_mask_cumulative = pygame.Mask((config.viewport_x, config.viewport_y))

    def gridify(self):
        self.grid = [] #map of costs
        for y in range(int(config.viewport_y/config.corridor_width)):
            self.grid.append([])
            for x in range(int(config.viewport_x/config.corridor_width)):
                overlaps_room = bool(self.rooms_mask.overlap(self.space,
                                                             (x*config.corridor_width,
                                                              y*config.corridor_width)))
                occupied = float("inf") if overlaps_room else 1
                self.grid[y].append(occupied)
        print(self.grid)

    def get_path(self, a, b, slope):
        if self.grid is None:
            self.update_rooms_mask()
            self.gridify()
        a_doors = [self.room_lookup[a].get_door(slope)]
        b_doors = [self.room_lookup[b].get_door(slope, b_room=True)]
        for door in a_doors+b_doors:
            print(door)
            self.corridor_mask_cumulative.draw(self.space, door)
        starts = [self.get_grid_pos(door) for door in a_doors]
        all_goals = [self.get_grid_pos(door) for door in b_doors]
        # for start in starts:
        #     for goal in goals:
        #         estimate = self.manhattan(start,goal)
        #         heapq.heappush(queue, (estimate, 0, start, (-1, -1)))
        self.calcs = 0
        candidates = []
        for start in starts:
            visited = {} # position: (cost, previous)
            queue = [] # (cost+estimate, cost, position)
            goals = all_goals.copy()
            for goal in goals:
                estimate = self.manhattan(start,goal)
                if self.visualizer_queue:
                    self.visualizer_queue.put(methodcaller("new_vertex",
                                                        Vertex(goal[0]*config.corridor_width,
                                                                goal[1]*config.corridor_width),
                                                        active=True, reset_active=False))
            pos = None
            heapq.heappush(queue, (estimate, 0, start, (-1, -1)))
            while queue and goals:
                _, cost, pos, previous = heapq.heappop(queue)

                if not pos in visited:
                    visited[pos] = (cost, previous)
                    # if self.visualizer_queue:
                    #     self.visualizer_queue.put(methodcaller("new_vertex",
                    #                                         Vertex(pos[0]*config.corridor_width,
                    #                                                 pos[1]*config.corridor_width),
                    #                                         active=False, reset_active=False))
                else:
                    continue
                for neighbor in self.neighbors(pos):
                    if neighbor in goals:
                        candidates.append((cost, pos))
                        pos = neighbor
                        goals.remove(neighbor)
                        print("visited length",len(visited))
                        continue
                    for goal in goals:
                        estimate = self.manhattan(neighbor, goal)
                        new_cost = cost + self.grid[neighbor[1]][neighbor[0]]
                        heapq.heappush(queue, (new_cost + estimate, new_cost, neighbor, pos))
                        self.calcs += 1
        candidates.sort()
        print(candidates)
        print(self.calcs,"calculations done :X")
        try:
            pos = candidates[0][1]
            path = []
            while pos != (-1,-1):
                self.grid[pos[1]][pos[0]] = 0
                px_pos = pos[0] * config.corridor_width, pos[1] * config.corridor_width
                path.append(px_pos)
                if self.visualizer_queue:
                    self.visualizer_queue.put(methodcaller("new_vertex", Vertex(px_pos[0], px_pos[1]),
                                                        active=True, reset_active=False))
                _, pos = visited[pos]
        except IndexError:
            return [(0,0)]
        return path

    def get_path_all_at_once(self, a, b):
        if self.grid is None:
            self.update_rooms_mask()
            self.gridify()
        visited = {} # position: (cost, previous)
        queue = [] # (cost+estimate, cost, position)
        starts = [self.get_grid_pos(door) for door in self.room_lookup[a].get_doors()]
        goals = [self.get_grid_pos(door) for door in self.room_lookup[b].get_doors()]
        for start in starts:
            for goal in goals:
                estimate = self.manhattan(start,goal)
                heapq.heappush(queue, (estimate, 0, start, (-1, -1)))
        candidates = []
        calcs = 4
        pos = None
        while queue and len(goals) > 2:
            _, cost, pos, previous = heapq.heappop(queue)
            # inf reset here?

            if not pos in visited:
                visited[pos] = (cost, previous)
                if self.visualizer_queue:
                    self.visualizer_queue.put(methodcaller("new_vertex",
                                                        Vertex(pos[0]*config.corridor_width,
                                                                pos[1]*config.corridor_width),
                                                        active=False, reset_active=False))
            else:
                continue
            for neighbor in self.neighbors(pos):
                if neighbor in goals:
                    candidates.append((cost, pos))
                    pos = neighbor
                    goals.remove(neighbor)
                    print("visited length",len(visited))
                    continue
                for goal in goals:
                    estimate = self.manhattan(neighbor, goal)
                    new_cost = cost + self.grid[neighbor[1]][neighbor[0]]
                    heapq.heappush(queue, (new_cost + estimate, new_cost, neighbor, pos))
                    calcs += 1
        candidates.sort()
        print(candidates)
        pos = candidates[0][1]
        path = []
        print(calcs,"calculations done :X")
        while pos is not (-1,-1):
            self.grid[pos[1]][pos[0]] = 0
            px_pos = pos[0] * config.corridor_width, pos[1] * config.corridor_width
            path.append(px_pos)
            if self.visualizer_queue:
                self.visualizer_queue.put(methodcaller("new_vertex", Vertex(px_pos[0], px_pos[1]),
                                                       active=True, reset_active=False))
            _, pos = visited[pos]
        return path

    def get_grid_pos(self, free_pos):
        return (int(round(free_pos[0] / config.corridor_width)),
                int(round(free_pos[1] / config.corridor_width)))

    def neighbors(self, pos):
        neighbors = [(pos[0]+1, pos[1]),
                     (pos[0]-1, pos[1]),
                     (pos[0], pos[1]+1),
                     (pos[0], pos[1]-1)]
        valid_neighbors = []
        for neigh in neighbors:
            if 0 <= neigh[0] < len(self.grid[0]) and 0 <= neigh[1] < len(self.grid):
                valid_neighbors.append(neigh)
        return valid_neighbors

    def euclidean(self, a, b):
        return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    def manhattan(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def is_valid_position(self, pos):
        overlap, reached = self.rooms_mask.overlap(self.space, pos), self.goal_reached(pos)
        return not overlap or reached

    def goal_reached(self, pos):
        reached = self.goal_mask.overlap(self.space, pos)
        return reached

    def draw_collision_overlay(self, viewport):
        overlay = self.corridor_mask_cumulative.to_surface(setcolor=(200, 0, 0, 100),
                                                       unsetcolor=(0, 0, 0, 0))
        overlay2 = self.rooms_mask.to_surface(setcolor=(0,0,170,127),
                                              unsetcolor=(0,0,0,0))
        viewport.blit(overlay, (0,0))
        viewport.blit(overlay2, (0,0))

    def centerify(self, point):
        return point[0]-config.corridor_width, point[1]-config.corridor_width

    def update_rooms_mask(self):
        for room in self.room_lookup.values():
            self.rooms_mask.draw(room.get_mask_with_margin(config.corridor_width/2),
                                 room.get_mask_offset(config.corridor_width/2))
