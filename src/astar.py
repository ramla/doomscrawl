import heapq
from math import floor, ceil
from operator import methodcaller
import pygame
import config
from bowyer_watson import Vertex

class AStar:
    """ A* adaptation to find paths between rooms located on a fine coordinate system by
    abstracting the rooms to a grid first.

    Attributes:
        space: Using this corridor square sized mask to create the grid we operate A* in

        grid: The grid we operate A* in

        rooms_mask: Screen sized mask where rooms are added in place with their added corridor
            margin. Used with space to create grid.

        calcs: Number of estimate calculations done, or numbe rof queue items added. Cumulative
            for all of the corridor generations.

        iters: Number of loop iterations, or number of items picked from queue to process.
            Cumulative for all of the corridor generations.
    """
    def __init__(self, room_lookup, visualizer_queue=None):
        """Parameters:
            room_lookup: dictionary to find room objects in by their center coordinate

            visualizer_queue: optional visualizer queue for debug or to show area explored by
                A*
        """
        self.room_lookup = room_lookup
        self.visualizer_queue = visualizer_queue
        self.space = pygame.Mask((config.corridor_width, config.corridor_width), fill=True)
        self.grid = None
        self.rooms_mask = pygame.Mask((config.viewport_x, config.viewport_y))
        self.calcs = 0
        self.iters = 0

    def gridify(self):
        """Creating the grid to operate A* in. A total bodge."""
        self.grid = []
        for y in range(int(config.viewport_y/config.corridor_width)):
            self.grid.append([])
            for x in range(int(config.viewport_x/config.corridor_width)):
                xy_px = self.centerify((x*config.corridor_width, y*config.corridor_width))
                overlaps_room = bool(self.rooms_mask.overlap(self.space,
                                                             xy_px))
                occupied = float("inf") if overlaps_room else config.astar_step_cost
                self.grid[y].append(occupied)

    def get_path(self, a, b, slope):
        """The thick of the meat"""
        if self.grid is None:
            self.update_rooms_mask()
            self.gridify()
        start_tiles, goal_tiles = self.do_the_door_spaghetti(a, b, slope)
        start, goal = start_tiles[-1], goal_tiles[-1]
        visited = {} # position: (cost, previous)
        queue = [] # (cost+estimate, cost, iterator[to avoid sorting by position], pos, prev_pos)
        estimate = self.manhattan(start,goal)
        if self.visualizer_queue and config.astar_debug:
            px_goal, px_start = self.get_centerified_px_pos(goal), \
                                self.get_centerified_px_pos(start)
            self.visualizer_queue.put(methodcaller("new_vertex",
                                                Vertex(px_goal[0],
                                                        px_goal[1]),
                                                active=True, reset_active=False))
            self.visualizer_queue.put(methodcaller("new_vertex",
                                                Vertex(px_start[0],
                                                        px_start[1]),
                                                active=True, reset_active=False))
        pos = None
        heapq.heappush(queue, (estimate, 0, self.iters, start, (-1, -1)))
        while queue:
            self.iters += 1
            estimate, cost, _, pos, previous = heapq.heappop(queue)
            prev_cost, _ = visited.get(pos, (float("inf"), None))
            if prev_cost <= cost:
                continue
            visited[pos] = (cost, previous)
            if pos == goal:
                break
            if self.visualizer_queue and config.astar_debug:
                px_pos = self.get_px_pos(pos)
                self.visualizer_queue.put(methodcaller("new_vertex",
                                                       Vertex(px_pos[0], px_pos[1]),
                                                       active=False, reset_active=False))
            for neighbor in self.neighbors(pos):
                estimate = self.manhattan(neighbor, goal)
                new_cost = cost + self.grid[neighbor[1]][neighbor[0]]
                heapq.heappush(queue, (new_cost + estimate, new_cost, self.iters, neighbor, pos))
                self.calcs += 1
        print(f"A* corridor {a}-{b} done, cumulative {self.calcs} calculations " \
              f"{self.iters} loop iterations")
        path = [self.get_px_pos(pos) for pos in start_tiles+goal_tiles] # include extension of door
                                                                    # to path (gridification hack)
        while pos != start:
            self.grid[pos[1]][pos[0]] = config.astar_corridor_cost
            px_pos = self.get_px_pos(pos)
            path.append(px_pos)
            _, pos = visited[pos]
        if config.astar_debug:
            for pos in path:
                self.visualizer_queue.put(methodcaller("new_vertex", Vertex(*pos),
                                                        active=True, reset_active=False))
        return path

    def do_the_door_spaghetti(self, a, b, slope):
        """This mess fetches proto-doors that are certain to be located inside the room even in the
        hack of a grid-adaptation, but not meet in the middle altogether to avoid corridors pathing
        through rooms.
            The proto-doors are then snapped to grid and extended outward so that they lie outside
        the room-corridor margins applied in the grid.
            All of the positions are returned so that they can be included in the path so that the
        corridors visually connect to the room as well."""
        a_door, a_dir = self.room_lookup[a].get_door(slope)
        b_door, b_dir = self.room_lookup[b].get_door(slope, b_room=True)
        if config.astar_debug:
            for pos in [a_door, b_door]:
                self.visualizer_queue.put(methodcaller("new_vertex", Vertex(*pos),
                                                        active=False, reset_active=False))
        a_aligned, b_aligned = (self.align_to_grid(a_door[0], a_dir[0]),
                                self.align_to_grid(a_door[1], a_dir[1])), \
                               (self.align_to_grid(b_door[0], b_dir[0]),
                                self.align_to_grid(b_door[1], b_dir[1]))
        return self.extend_doors(a_aligned, a_dir, b_aligned, b_dir)

    def extend_doors(self, a, a_dir, b, b_dir):
        """Function that takes proto-door locations and extends them to a position with
        non-infinite cost."""
        a_tiles, b_tiles = [a], [b]
        while self.grid[a[1]][a[0]] > config.astar_step_cost:
            self.grid[a[1]][a[0]] = 1
            a = a[0] + a_dir[0], a[1] - a_dir[1]
            a_tiles.append(a)
        while self.grid[b[1]][b[0]] > config.astar_step_cost:
            self.grid[b[1]][b[0]] = 1
            b = b[0] + b_dir[0], b[1] - b_dir[1]
            b_tiles.append(b)
        if config.astar_debug:
            for point in a_tiles+b_tiles:
                point_px = self.get_px_pos(point)
                self.corridor_mask_cumulative.draw(self.space, self.centerify(point_px))
        return a_tiles, b_tiles

    def align_to_grid(self, value, direction):
        """Snaps [a proto-door] location to lie toward the inside of the room rather than toward
        the outside of it to reduce visual glitches"""
        scaled = value/config.corridor_width
        if direction > 0:
            return ceil(scaled)
        elif direction < 0:
            return floor(scaled)
        else:
            return round(scaled)

    def neighbors(self, pos):
        """Returns list of neighboring positions that lie within the grid"""
        neighbors = [(pos[0]+1, pos[1]),
                     (pos[0]-1, pos[1]),
                     (pos[0], pos[1]+1),
                     (pos[0], pos[1]-1)]
        valid_neighbors = []
        for neigh in neighbors:
            if 0 <= neigh[0] < len(self.grid[0]) and 0 <= neigh[1] < len(self.grid):
                valid_neighbors.append(neigh)
        return valid_neighbors

    def manhattan(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def draw_collision_overlay(self, viewport):
        """debug overlay function"""
        overlay = self.corridor_mask_cumulative.to_surface(setcolor=(200, 0, 0, 100),
                                                       unsetcolor=(0, 0, 0, 0))
        overlay2 = self.rooms_mask.to_surface(setcolor=(0,0,170,127),
                                              unsetcolor=(0,0,0,0))
        viewport.blit(overlay, (0,0))
        viewport.blit(overlay2, (0,0))

    def centerify(self, point, positive_delta=False):
        """Nudge a pixel coordinate up left or down right by half corridor width"""
        if positive_delta:
            return point[0]+config.corridor_width/2, point[1]+config.corridor_width/2
        return point[0]-config.corridor_width/2, point[1]-config.corridor_width/2

    def get_px_pos(self, pos):
        """Convert grid position to a top left corner pixel position"""
        return pos[0] * config.corridor_width, pos[1] * config.corridor_width

    def get_centerified_px_pos(self, pos, positive_delta=False):
        """Convert a grid position to a centered pixel position"""
        return self.centerify(self.get_px_pos(pos), positive_delta=positive_delta)

    def update_rooms_mask(self):
        """Fetches and stamps room masks extended with corridor margin to a single
        mask for use in grid generation"""
        for room in self.room_lookup.values():
            self.rooms_mask.draw(room.get_mask_with_margin(config.room_corridor_margin),
                                 room.get_mask_offset(config.room_corridor_margin))
