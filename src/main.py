from itertools import product
from game import Doomcrawl
from utility import get_random_points_int

default_size = (40,40)
rooms = None

# some edge cases to observe
# all points close to being on the same line
# roomlocs = [(518, 154), (99, 80), (324, 120), (607, 171)]
# roomlocs = [(11, 127), (124, 138), (1038, 219), (748, 199)]

# one triangle, one edge
# roomlocs = [(619, 53), (479, 53), (56, 56), (231, 47)]
# roomlocs = [(669, 135), (339, 124), (303, 140), (948, 138)]

# adding a point on circumcircle
# roomlocs = [(222, 99), (48, 61), (167, 33), (78, 36)]
# roomlocs = [(580,440), (300,160), (720,160), (300,300), (720,300)]
# roomlocs = list(product(range(100,1100,360), range(100,600,220)))

# I believe technically these point sets should result in concave triangulations
# (thus 3 triangles) but I'm letting it slide since in practice it is fine
# roomlocs = [(926, 55), (787, 55), (7, 51), (807, 59)]
# roomlocs = [(629, 583), (880, 636), (153, 486), (856, 478)]
# roomlocs = [(585, 584), (1006, 215), (745, 318), (165, 533)]
# roomlocs = [(269, 238), (585, 119), (430, 178), (182, 319)]
# roomlocs = [(145, 247), (768, 75), (261, 256), (603, 291)]
# roomlocs = [(594, 52), (682, 44), (410, 93), (184, 81)]
# --

roomlocs = get_random_points_int(15, (100,100), (1100,600))
rooms = list(zip(roomlocs, [default_size]*len(roomlocs)))

app = Doomcrawl(rooms)
app.start()
