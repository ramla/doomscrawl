import pygame

POINT_REJECTED = pygame.USEREVENT + 1

circumcircle_debug = False
collision_debug = False
room_debug = False  #print room list to terminal when passing room centers to 
                    #triangulation, among other things
bw_debug = False
problematic_point_debug = False
visualizer_debug = False
delay_visualisation = True
random_rooms = True
draw_coords = False

viewport_x = 1200
viewport_y = 700
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
    "fill1":    pygame.Color(175,67,25,31), # rusty spice
    "fill2":    pygame.Color(40,60,70,31),  # neutral fill
    "hilite1":  pygame.Color(89,195,195),   # strong cyan
    "hilite2":  pygame.Color(244,91,105),   # bubblegum pink
    "hilite3":  pygame.Color(237,240,96),   # canary yellow
    "dark1":    pygame.Color(180,25,60),    # rejection red
    "bg":       pygame.Color(20,23,30),     # ink black
    }
color_room = color["col1"]
color_tri = color["col2"]
color_tri_active = color["hilite3"]
color_edge = color["col2"]
color_edge_active = color["col4"]
color_vertex = color["col5"]
color_vertex_active = color["hilite2"]
color_vertex_rejected = color["dark1"]
color_circumcircle = color["col6"]
color_circumcircle_fill = color["fill2"]
color_circumcircle_final = color["col3"]

FONTFILE = "assets/WarsawGothic-BnBV.otf"

room_size_min = (thickness*3, thickness*3)
room_size_max = (viewport_x//4, viewport_y//3)

vertex_anim_duration = 1/60
if delay_visualisation:
    vertex_anim_duration = 0.3
vertex_anim_new_scale = 1.5
circumcircle_anim_duration = 1/60
if delay_visualisation:
    circumcircle_anim_duration = 3
circumcircle_anim_drop_scale = 0.95

vertex_radius = thickness/3
edge_width = thickness/5
triangle_width = thickness/5
corridor_width = thickness*1.5

visualisation_delay_min = 0
if delay_visualisation:
    visualisation_delay_min = 1/60

draw_final_circumcircles = True

player_speed = 20 * thickness

helptext_test = "Q, Esc        Next exception\n" \
                "Space         End visual checks\n"
helptext      = "Esc, Q        Quit\n" \
                "WASD        Move\n" \
                "      R          Randomise another room\n" \
                "      E          Step triangulation\n" \
                "      T          Triangulate all\n" \
                "      F          Next phase\n" \
                "    F1 or H to display this again\n" \
                "        any key to continue"
