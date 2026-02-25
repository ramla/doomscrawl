import getopt
import sys
import ast
from itertools import product
from game import Doomcrawl
from utility import get_random_points_int
from dungeon import Room
import config

DEFAULT_SIZE = (30,30)
rooms = None
super_triangle = None

args = sys.argv[1:]
options = "tr:s:"
long_options = ["no_freetype", "rooms=", "super="]
try:
    arguments, values = getopt.getopt(args, options, long_options)
    for currentArg, currentVal in arguments:
        if currentArg in ("-t", "--no_freetype"):
            print("Running in freetype compatibility mode: help text and coordinate rendering disabled")
        elif currentArg in ("-r", "--rooms="):
            roomlocs = ast.literal_eval(currentVal)
            rooms = list(zip(roomlocs, [DEFAULT_SIZE]*len(roomlocs)))
        elif currentArg in ("-s", "--super="):
            try:
                super_triangle = ast.literal_eval(currentVal)
            except IndexError:
                if super_triangle is None:
                    print("No points given for super triangle, using test case values")
                    super_triangle = [(-1100, -950), (-1100, 1700), (2400, 350)]
    if super_triangle and rooms is None:
        print("No room locations given, using test case values A to F")
        roomlocs = [(643, 223), (159, 539), (379, 531), (861, 527), (399, 221), (420, 400)]
        rooms = list(zip(roomlocs, [DEFAULT_SIZE]*len(roomlocs)))
except getopt.error as err:
    print(str(err))

# some edge cases to observe
# all points close to being on the same line
# roomlocs = [(518, 154), (99, 80), (324, 120), (607, 171)]
# roomlocs = [(11, 127), (124, 138), (1038, 219), (748, 199)]

# one triangle, one edge
# roomlocs = [(619, 53), (479, 53), (56, 56), (231, 47)]

# adding a point on circumcircle
# roomlocs = [(222, 99), (48, 61), (167, 33), (78, 36)]
# roomlocs = [(580,440), (300,160), (720,160), (300,300), (720,300)]
# roomlocs = [(650, 50), (650, 410), (50, 290), (890, 50), (890, 410), (1010, 170), (1010, 530), (170, 50), (170, 410), (770, 170), (290, 170), (290, 530), (770, 530), (1130, 290), (650, 290), (410, 290), (530, 170), (50, 530), (50, 170), (530, 530), (1010, 50), (1010, 410), (530, 290), (770, 50), (770, 410), (890, 290), (170, 290), (290, 50), (290, 410), (1130, 170), (1130, 530), (410, 50), (530, 50), (530, 410), (650, 170), (650, 530), (410, 170), (410, 530), (50, 410), (50, 50), (890, 170), (890, 530), (1010, 290), (1130, 410), (770, 290), (290, 290), (170, 170), (170, 530), (1130, 50), (410, 410)]
# roomlocs = list(product(range(100,1100,360), range(100,600,220)))

# I believe technically these point sets should result in concave triangulations
# (thus 3 triangles) but I'm letting it slide since in practice it is fine
# roomlocs = [(629, 583), (880, 636), (153, 486), (856, 478)]
# roomlocs = [(585, 584), (1006, 215), (745, 318), (165, 533)]
# roomlocs = [(269, 238), (585, 119), (430, 178), (182, 319)]
# roomlocs = [(145, 247), (768, 75), (261, 256), (603, 291)]
# --

# (barely) concave triangulations
# roomlocs = [(140, 136), (506, 268), (1112, 451), (804, 370), (1080, 98), (760, 475), (940, 579)]

# n = 30
# roomlocs = get_random_points_int(n, (100,100), (1100,600))
# rooms = list(zip(roomlocs, [DEFAULT_SIZE]*len(roomlocs)))
# roomsizes = [Room.get_random_size("") for _ in range(len(roomlocs))]
# rooms = list(zip(roomlocs, roomsizes))

app = Doomcrawl(rooms, super_tri=super_triangle)
app.start()
