import pygame

collision_debug = False

viewport_x = 800
viewport_y = 600

thickness = 15
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
