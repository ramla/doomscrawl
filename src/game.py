import sys
from enum import Enum, auto
import pygame

import config
if not config.freetype_compatibility_mode:
    import pygame.freetype

from dungeon import Dungeon
from player import Player
from bowyer_watson import BowyerWatson
from visualizer import Visualizer
from prims import prims


class Doomcrawl:
    def __init__(self, rooms=None, add_title=None, exceptions=False, super_tri=None):
        pygame.init()
        self.viewport = pygame.display.set_mode((config.viewport_x,config.viewport_y),
                                                pygame.RESIZABLE)
        title = "Doomscrawl"
        if add_title is not None:
            title = "Doomscrawl - " + add_title
        self.visually_confirm_test_exceptions = False
        if exceptions:
            self.visually_confirm_test_exceptions = True
        pygame.display.set_caption(title)
        if not config.freetype_compatibility_mode:
            pygame.freetype.init()
            self.font = pygame.freetype.Font(config.FONTFILE, config.thickness * 3)
            self.help_surface = self.create_help_surface()
        else:
            self.help_surface = pygame.Surface((1,1))

        if rooms:
            config.random_rooms = False
        self.visualizer = Visualizer(self.viewport)
        self.dungeon = Dungeon((config.viewport_x, config.viewport_y), rooms, exceptions,
                               self.visualizer.event_queue)
        self.player = Player(self.dungeon.player_start_pos, (config.thickness, config.thickness))
        self.bw = BowyerWatson(visualizer_queue=self.visualizer.event_queue, super_tri=super_tri)
        self.state_machine = StateMachine()
        self.running = True
        self.helping = True
        self.pruned_edges = None

    def start(self):
        if self.visually_confirm_test_exceptions:
            config.delay_visualisation = False
            self.bw.add_points(self.dungeon.get_room_centers())
            self.bw.triangulate_all()
        self.loop(config.target_fps)
        sys.exit()

    def loop(self, target_fps):
        clock = pygame.time.Clock()
        while self.running:
            frame_time = clock.tick(target_fps) / 1000

            self.process_events()
            self.process_key_input()

            self.player.clamp_ip(self.viewport.get_rect())

            self.viewport.fill(config.color["bg"])

            self.dungeon.draw_dungeon(self.viewport, frame_time)

            match self.state_machine.get():
                case GameState.STEPPING:
                    if self.bw.ready and len(self.bw.next_points) == 0:
                        self.bw.add_points(points=self.dungeon.get_room_centers())
                    else:
                        self.bw.iterate_once()
                        self.state_machine.set(GameState.STEPPED)
                    if self.bw.ready and self.visualizer.event_queue.empty():
                        self.state_machine.set(GameState.TRIANGULATED)
                case GameState.TRIANGULATING:
                    if self.visualizer.event_queue.empty():
                        if self.bw.ready and len(self.bw.next_points) == 0:
                            self.bw.add_points(self.dungeon.get_room_centers())
                        else:
                            self.visualizer.method_to_queue("clear_entities_by_type",
                                                            circumcircles=True)
                            self.bw.iterate_once()
                        if self.bw.ready:
                            self.state_machine.set(GameState.TRIANGULATED)

            self.visualizer.visualize(frame_time)

            pygame.draw.rect(self.viewport, config.color["hilite1"], self.player)

            if config.collision_debug:
                self.dungeon.draw_collision_overlay(self.viewport)
                self.player.draw_collision_overlay(self.viewport)
                self.dungeon.astar.draw_collision_overlay(self.viewport)

            if self.helping:
                self.show_help()

            pygame.display.flip()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self.helping = False
                if event.key == pygame.K_r:
                    if self.state_machine.get() == GameState.READY:
                        self.dungeon.add_room()
                if event.key == pygame.K_t:
                    try:
                        self.state_machine.set(GameState.TRIANGULATING)
                    except ValueError:
                        pass
                if event.key == pygame.K_F1 or \
                   event.key == pygame.K_h:
                    self.helping = True
                if event.key == pygame.K_f:
                    if self.state_machine.get() in [GameState.READY, GameState.STEP_CLEARED]:
                        self.state_machine.set(GameState.STEPPING)
                    elif self.state_machine.get() == GameState.TRIANGULATED:
                        self.visualizer.method_to_queue("clear_final_view", self.bw.final_edges)
                        self.state_machine.set(GameState.CCS_CLEARED)
                    elif self.state_machine.get() == GameState.STEPPED:
                        self.visualizer.method_to_queue("clear_entities_by_type",
                                                        circumcircles=True)
                        if self.bw.ready:
                            self.state_machine.set(GameState.TRIANGULATED)
                        else:
                            self.state_machine.set(GameState.STEP_CLEARED)
                    elif self.state_machine.get() == GameState.CCS_CLEARED:
                        self.pruned_edges = self.get_pruned_edges(self.bw.final_edges,
                                            start_at=self.dungeon.get_player_room_center())
                        # self.pruned_edges = self.bw.final_edges
                        self.visualizer.method_to_queue("redraw_edges", self.pruned_edges)
                        self.state_machine.set(GameState.PRUNED)
                    elif self.state_machine.get() == GameState.PRUNED:
                        self.dungeon.create_corridors(self.pruned_edges)
                        self.state_machine.set(GameState.CONNECTED)
                    elif self.state_machine.get() == GameState.CONNECTED:
                        #clear corridors here?
                        self.state_machine.set(GameState.READY)
                if event.key == pygame.K_0:
                    config.collision_debug = not config.collision_debug
            if event.type == config.POINT_REJECTED:
                self.dungeon.handle_point_rejection(event.room_center)

    def process_key_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.dungeon.collision_mask.overlap(self.player.collision_mask,
                                    (self.player.x - self.player.speed - self.player.size[0],
                                     self.player.y)):
                self.player.move_ip(-self.player.speed, 0)
            elif config.collision_debug:
                print("colliding left")
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.dungeon.collision_mask.overlap(self.player.collision_mask,
                                    (self.player.x + self.player.speed + self.player.size[0],
                                     self.player.y)):
                self.player.move_ip(self.player.speed, 0)
            elif config.collision_debug:
                print("colliding right")
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.dungeon.collision_mask.overlap(self.player.collision_mask,
                                    (self.player.x,
                                     self.player.y - self.player.speed - self.player.size[1])):
                self.player.move_ip(0, -self.player.speed)
            elif config.collision_debug:
                print("colliding up")
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if self.dungeon.collision_mask.overlap(self.player.collision_mask,
                                    (self.player.x,
                                     self.player.y + self.player.speed + self.player.size[1])):
                self.player.move_ip(0, self.player.speed)
            elif config.collision_debug:
                print("colliding down")

        if keys[pygame.K_q] or keys[pygame.K_ESCAPE]:
            self.running = False
        if keys[pygame.K_SPACE] and self.visually_confirm_test_exceptions:
            raise SystemExit(1)

    def create_help_surface(self):
        help_surface = pygame.Surface((config.viewport_x, config.viewport_y), pygame.SRCALPHA)
        text = config.helptext
        if self.visually_confirm_test_exceptions:
            text = config.helptext_test
        line_height = self.font.get_sized_height()
        x, y = config.thickness * 4, config.thickness * 3
        for line in text.splitlines():
            self.font.render_to(help_surface, (x, y),
                                line, config.color["light1"])
            y += line_height + config.thickness / 2

        return help_surface

    def show_help(self):
        self.viewport.blit(self.help_surface, (0,0))

    def get_pruned_edges(self, bw_edges, start_at=None):
        nodes = set()
        edges = []
        for edge in bw_edges:
            a, b = edge.get_coords()
            weight = edge.get_length()
            nodes.update([a,b])
            edges.append((a, b, weight))
        mst = prims(list(nodes), edges, start_at=start_at)
        mst = [tuple(sorted(x)) for x in mst]
        edge_objects = [edge for edge in bw_edges if edge.get_coords() in mst]
        return edge_objects


class GameState(Enum):
    READY = auto()
    STEPPING = auto()
    STEPPED = auto()
    STEP_CLEARED = auto()
    TRIANGULATING = auto()
    TRIANGULATED = auto()
    CCS_CLEARED = auto()
    PRUNED = auto()
    CONNECTED = auto()

TRANSITIONS = {
    GameState.READY:            {GameState.TRIANGULATING,
                                 GameState.STEPPING},
    GameState.TRIANGULATING:    {GameState.TRIANGULATING,
                                 GameState.STEPPING,
                                 GameState.TRIANGULATED},
    GameState.STEPPING:         {GameState.TRIANGULATING,
                                 GameState.STEPPED,
                                 GameState.TRIANGULATED},
    GameState.STEPPED:          {GameState.TRIANGULATING,
                                 GameState.STEP_CLEARED,
                                 GameState.TRIANGULATED},
    GameState.STEP_CLEARED:     {GameState.TRIANGULATING,
                                 GameState.STEPPING,
                                 GameState.TRIANGULATED},
    GameState.TRIANGULATED:     {GameState.READY, GameState.CCS_CLEARED, GameState.PRUNED},
    GameState.CCS_CLEARED:          {GameState.READY, GameState.PRUNED},
    GameState.PRUNED:           {GameState.READY, GameState.CONNECTED},
    GameState.CONNECTED:        {GameState.READY}
}

class StateMachine:
    def __init__(self):
        self.__state__ = GameState.READY

    def set(self, new_state):
        if new_state in TRANSITIONS[self.__state__]:
            self.__state__ = new_state
            print(new_state)
        else:
            raise ValueError

    def get(self):
        return self.__state__
