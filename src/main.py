from itertools import product
from game import Doomcrawl

default_size = (40,40)
rooms = None
# rooms = [((200,200), default_size),
        #  ((300,300), default_size),
        #  ((300,600), default_size),
        #  ((600,600), default_size),
        #  ((600,250), default_size),
        #  ]
# roomlocs = list(product(range(20,1000,140), range(20,660,140)))
# roomlocs = ((580,440), (300,160), (720,160), (300,300), (720,300))
# roomlocs = tuple(sorted(list(((559, 115), (96, 451), (358, 463), (956, 457))))) #(596, 370), (857, 291), 
# rooms = list(zip(roomlocs, [default_size]*len(roomlocs)))
app = Doomcrawl(rooms)
app.start()
