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
roomlocs = ((720,20), (580,440), (20,20), (300,160), (720,160), (20,160), (580, 580), (300,300), (720,300))
rooms = list(zip(roomlocs, [default_size]*len(roomlocs)))
app = Doomcrawl(rooms)
app.start()
