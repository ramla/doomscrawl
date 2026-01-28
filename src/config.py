import pygame

collision_debug = False
room_debug = False
visualizer_debug = False

viewport_x = 1800
viewport_y = 1000
target_fps = 60

thickness = min(viewport_x, viewport_y) // 40
super_tri_margin = thickness * 2

color = {
    "light1":   pygame.Color(235,235,235),  # platinum
    "col1":     pygame.Color(82,72,156),    # dusty grape
    "col2":     pygame.Color(64,98,187),    # smart blue
    "hilite1":  pygame.Color(89,195,195),   # strong cyan
    "hilite2":  pygame.Color(244,91,105),   # bubblegum pink
    "hilite3":  pygame.Color(237,240,96),   # canary yellow
    "bg":       pygame.Color(20,23,30),     # ink black
    }

room_size_min = (thickness*3, thickness*3)
room_size_max = (viewport_x//4, viewport_y//3)

visualisation_delay_min = 1/60
vertex_anim_duration = 0.3
vertex_anim_pop_scale = 1.5
vertex_radius = thickness/3
edge_width = thickness/7
triangle_width = thickness/5

player_speed = 20 * thickness
