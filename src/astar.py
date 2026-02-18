import heapq
from operator import methodcaller
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
        start = self.room_lookup[a].get_door(slope)
        self.goal = self.room_lookup[b].get_door(slope, b_room=True)
        self.goal_mask = pygame.Mask((config.viewport_x, config.viewport_y))
        self.goal_mask.draw(self.space, self.goal)
        self.goal_mask_cumulative.draw(self.space, self.goal)

        path = set()
        prev_pos_in_path = False
        queue = [(self.squared_euclidean(a, b), start)]
        heapq.heapify(queue)
        print(f"nyt päästiin asiaan {a}, {b}, {slope}")
        while len(queue) > 0:
            _, pos = heapq.heappop(queue)
            print("tässäkin ollaa")
            if self.visualizer_queue:
                self.visualizer_queue.put(methodcaller("new_vertex", Vertex(pos[0], pos[1]),
                                                       active=True, reset_active=True))
            if self.goal_reached(pos):
                print("GOAL REACHED FRFR")
                return path
            if pos in path and prev_pos_in_path:
                path.remove(pos)
            elif pos in path:
                prev_pos_in_path = True
            else:
                prev_pos_in_path = False
                path.add(pos)
            for neighbor in self.neighbors(pos):
                distance = self.squared_euclidean(neighbor, self.goal)
                print("new neighbor",neighbor,distance)
                heapq.heappush(queue, (distance, neighbor))
        return path

    def neighbors(self, pos):
        step = config.corridor_width
        neighbors = ((pos[0]+step, pos[1]),
                     (pos[0]-step, pos[1]),
                     (pos[0], pos[1]+step),
                     (pos[0], pos[1]-step))
        neibs = [new_pos for new_pos in neighbors if self.is_valid_position(new_pos)]
        print(neibs)
        return neibs

    def squared_euclidean(self, a, b):
        """squared distance"""
        return (a[0]-b[0])**2 + (a[1]-b[1])**2

    def blocky_distance(self, a, b):
        return a[0]-b[0] + a[1]-b[1]

    def is_valid_position(self, pos):
        overlap, reached = self.dungeon_mask.overlap(self.space, pos), self.goal_reached(pos)
        print(f"overlap/reached {overlap}/{reached}")
        return not overlap or reached

    def goal_reached(self, pos):
        reached = self.goal_mask.overlap(self.space, pos)
        if reached:
            print("goal reached")
        return reached

    def draw_collision_overlay(self, viewport):
        overlay = self.goal_mask_cumulative.to_surface(setcolor=(200, 0, 0, 100),
                                                       unsetcolor=(0, 0, 0, 0))
        viewport.blit(overlay, (0,0))

# grid_size = (config.viewport_x//space_size_px[0], config.viewport_y//space_size_px[1])
# start = (a[0]//grid_size[0], a[1]//grid_size[1])
# goal = (b[0]//grid_size[0], b[1]//grid_size[1])

# delta_x, delta_y = (a[0]-b[0]), (a[1]-b[1])

# to_visit = Q.PriorityQueue()
# to_visit.put(State(start, time_of_beginning))

# best_route_time = float("inf")
# best_route = None

# while not to_visit.empty():
#     current_state = to_visit.get()
#     current_stop_code = current_state.get_stop_code()
#     neighboring_stops_codes = self.get_neighbors_codes(current_stop_code)
#     for next_stop_code in neighboring_stops_codes:
#         ftt = self.fastest_transition(current_stop_code,next_stop_code,current_state.get_time())
#         next_time = current_state.get_time() + ftt
#         if next_time > best_route_time:
#             continue
#         if next_stop_code == current_state.goal["code"]:
#             if next_time < best_route_time:
#                 best_route = (State(self.get_stop(next_stop_code), next_time, current_state))
#                 best_route_time = next_time
#         else:
#             to_visit.put(State(self.get_stop(next_stop_code), next_time, current_state))
# return best_route