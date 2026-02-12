# from itertools import product
from game import Doomcrawl

default_size = (40,40)
rooms = None

# roomlocs = list(product(range(20,1000,140), range(20,660,140)))
# roomlocs = ((580,440), (300,160), (720,160), (300,300), (720,300))

# I believe technically these point sets should result in concave triangulations
# (thus 3 triangles) but I'm letting it slide since in practice it is fine
# roomlocs = [(926, 55), (787, 55), (7, 51), (807, 59)]
# roomlocs = [(629, 583), (880, 636), (153, 486), (856, 478)]
# roomlocs =  [(585, 584), (1006, 215), (745, 318), (165, 533)]
# roomlocs = [(269, 238), (585, 119), (430, 178), (182, 319)]
# roomlocs = [(145, 247), (768, 75), (261, 256), (603, 291)]
# roomlocs = [(594, 52), (682, 44), (410, 93), (184, 81)]
# --

# rooms = list(zip(roomlocs, [default_size]*len(roomlocs)))

app = Doomcrawl(rooms)
app.start()
