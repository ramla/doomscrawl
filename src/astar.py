import heapq
from math import sqrt, floor, ceil, log
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
        self.calcs = 0
        self.iters = 0

    def gridify(self):
        self.grid = [] #map of costs
        for y in range(int(config.viewport_y/config.corridor_width)):
            self.grid.append([])
            for x in range(int(config.viewport_x/config.corridor_width)):
                overlaps_room = bool(self.rooms_mask.overlap(self.space,
                                                             (x*config.corridor_width,
                                                              y*config.corridor_width)))
                occupied = 10 if overlaps_room else 1
                self.grid[y].append(occupied)

    def get_path(self, a, b, slope):
        if self.grid is None:
            self.update_rooms_mask()
            self.gridify()
        start, start_dir, goal, finish_dir = self.do_the_door_spaghetti(a, b, slope)
        candidates = []
        # visited = { start: (-1, (-1, -1)) }
        visited = {} # position: (cost, previous)
        queue = [] # (cost+estimate, cost, position)
        best_cost = float("inf")
        estimate = self.manhattan(start,goal)
        halfway = self.get_halfway(start,goal)
        #pitää tehä halfway x halfway y!!!!!!!!!!
        if self.visualizer_queue:
            px_goal, px_start = self.get_px_pos(goal), self.get_px_pos(start)
            self.visualizer_queue.put(methodcaller("new_vertex",
                                                Vertex(px_goal[0],
                                                        px_goal[1]),
                                                active=True, reset_active=False))
            self.visualizer_queue.put(methodcaller("new_vertex",
                                                Vertex(px_start[0],
                                                        px_start[1]),
                                                active=True, reset_active=False))
        pos = None
        heapq.heappush(queue, (estimate, 0, start, (-1, -1)))
        while queue:
            self.iters += 1
            estimate, cost, pos, previous = heapq.heappop(queue)
            if estimate > best_cost:
                print("let's not go here?")
                continue
            if pos in visited:
                if cost < visited[pos][0]:
                    print("this surely isn't happening at least until combined corridors")
                else:
                    continue
            visited[pos] = (cost, previous)
            if self.visualizer_queue:
                px_pos = self.get_centerified_px_pos(pos)
                if config.astar_debug:
                    self.visualizer_queue.put(methodcaller("new_vertex",
                                                           Vertex(px_pos[0], px_pos[1]),
                                                           active=False, reset_active=False))
            for neighbor, estimate in self.weighed_neighbors(pos, halfway, goal,
                                                             start_dir, finish_dir):
                if neighbor == goal:
                    candidates.append((cost, pos))
                    visited[neighbor] = (cost, pos)
                    best_cost = cost
                    # queue = []
                new_cost = cost + self.grid[neighbor[1]][neighbor[0]]
                heapq.heappush(queue, (new_cost + estimate, new_cost, neighbor, pos))
                self.calcs += 1
        candidates.sort()
        print(candidates)
        print(self.calcs,"calculations done",self.iters,"loop iterations")
        pos = candidates[0][1]
        path = []
        while pos != start:
            print(visited[pos])
            # self.grid[pos[1]][pos[0]] = 0
            px_pos = self.get_px_pos(pos)
            path.append(px_pos)
            if self.visualizer_queue:
                self.visualizer_queue.put(methodcaller("new_vertex", Vertex(px_pos[0], px_pos[1]),
                                                       active=True, reset_active=False))
            _, pos = visited[pos]
        path.append(start)
        return path

    def get_halfway(self, a, b):
        return abs(a[0]-b[0])//2, abs(a[1]-b[1])//2

    def do_the_door_spaghetti(self, a, b, slope):
        a_door, a_dir = self.room_lookup[a].get_door(slope)
        b_door, b_dir = self.room_lookup[b].get_door(slope, b_room=True)
        a_aligned, b_aligned = (self.align_to_grid(a_door[0], a_dir[0]),
                                self.align_to_grid(a_door[1], a_dir[1])), \
                               (self.align_to_grid(b_door[0], b_dir[0]),
                                self.align_to_grid(b_door[1], b_dir[1]))
        a_final, b_final = self.extend_doors(a_aligned, a_dir, b_aligned, b_dir)
        return a_final, a_dir, b_final, (b_dir[0]*-1, b_dir[1]*-1)

    def extend_doors(self, a, a_dir, b, b_dir):
        points_to_draw = []
        while self.rooms_mask.overlap(self.space, a):
            points_to_draw.append(a)
            a = a[0] + a_dir[0], a[1] + a_dir[1]
        while self.rooms_mask.overlap(self.space, b):
            points_to_draw.append(b)
            b = b[0] + b_dir[0], b[1] + b_dir[1]
        for point in points_to_draw:
            point_px = self.get_px_pos(point)
            self.corridor_mask_cumulative.draw(self.space, self.centerify(point_px))
        return a, b

    def align_to_grid(self, value, direction):
        scaled = value/config.corridor_width
        if direction > 0:
            return ceil(scaled)
        elif direction < 0:
            return floor(scaled)
        else:
            return round(scaled)

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

    def weighed_neighbors(self, pos, halfway, goal, start_dir, finish_dir):
        xy_progress = abs(pos[0]-goal[0]), abs(pos[1]-goal[1])
        halfway_reached = xy_progress[0] - halfway[0] > 0 or xy_progress[1] - halfway[1] > 0
        weights = 4 * [0.5 - 1 * halfway_reached]
        dirs = [(1,0), (0,1), (-1,0), (0,-1)]
        if halfway_reached:
            weights[dirs.index(finish_dir)] *= -1
            weights[dirs.index((finish_dir[0]*-1, finish_dir[1]*-1))] *= -1
        else:
            weights[dirs.index(start_dir)] *= -1
        neighbors = [(pos[0]+1, pos[1]),
                     (pos[0], pos[1]+1),
                     (pos[0]-1, pos[1]),
                     (pos[0], pos[1]-1)]
        valid_neighbors = []
        for i in range(4):
            neigh = neighbors[i]
            if 0 <= neigh[0] < len(self.grid[0]) and 0 <= neigh[1] < len(self.grid):
                estimate = self.manhattan(neigh, goal) + weights[i]
                valid_neighbors.append((neigh, estimate))
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

    def centerify(self, point, positive_delta=False):
        if positive_delta:
            return point[0]+config.corridor_width/2, point[1]+config.corridor_width/2
        return point[0]-config.corridor_width/2, point[1]-config.corridor_width/2

    def get_px_pos(self, pos):
        return pos[0] * config.corridor_width, pos[1] * config.corridor_width

    def get_centerified_px_pos(self, pos, positive_delta=False):
        return self.centerify(self.get_px_pos(pos), positive_delta=positive_delta)

    def update_rooms_mask(self):
        for room in self.room_lookup.values():
            self.rooms_mask.draw(room.get_mask_with_margin(config.corridor_width/2),
                                 room.get_mask_offset(config.corridor_width/2))
