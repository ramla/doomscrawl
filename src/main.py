from game import Doomcrawl

default_size = (100,100)
rooms = None
# rooms = [((200,200), default_size),
        #  ((300,300), default_size),
        #  ((300,600), default_size),
        #  ((600,600), default_size),
        #  ((600,250), default_size),
        #  ]
app = Doomcrawl(rooms)
app.start()
