import pygame

collision_debug = False
room_debug = False  #print room list to terminal when passing room centers to 
                    #triangulation, among other things
visualizer_debug = False
delay_visualisation = True
random_rooms = True

viewport_x = 1800
viewport_y = 1000
target_fps = 60

thickness = min(viewport_x, viewport_y) // 40
super_tri_margin = thickness * 2

color = {
    "light1":   pygame.Color(235,235,235),  # platinum
    "col1":     pygame.Color(82,72,156),    # dusty grape
    "col2":     pygame.Color(64,98,187),    # smart blue
    "col3":     pygame.Color(74,25,66),     # blackberry cream
    "col4":     pygame.Color(9,161,41),     # medium jungle
    "col5":     pygame.Color(112,3,83),     # crimson violet
    "col6":     pygame.Color(119,32,20),    # dark wine
    "fill1":    pygame.Color(175,67,25,31),# rusty spice
    "hilite1":  pygame.Color(89,195,195),   # strong cyan
    "hilite2":  pygame.Color(244,91,105),   # bubblegum pink
    "hilite3":  pygame.Color(237,240,96),   # canary yellow
    "bg":       pygame.Color(20,23,30),     # ink black
    }
color_tri = color["col2"]
color_tri_active = color["hilite3"]
color_edge = color["col3"]
color_edge_active = color["col4"]
color_vertex = color["col5"]
color_vertex_active = color["hilite2"]
color_circumcircle = color["col6"]
color_circumcircle_fill = color["fill1"]

room_size_min = (thickness*3, thickness*3)
room_size_max = (viewport_x//4, viewport_y//3)

vertex_anim_duration = 0.3
vertex_anim_pop_scale = 1.5
vertex_radius = thickness/3
edge_width = thickness/7
triangle_width = thickness/5
visualisation_delay_min = 0
if delay_visualisation:
    visualisation_delay_min = 1/60

player_speed = 20 * thickness
