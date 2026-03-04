
import unittest
from dungeon import Dungeon

class TestDungeon(unittest.TestCase):
    def setUp(self):
        self.dungeon = Dungeon()

class TestAStar(unittest.TestCase):
      def setUp(self):
        self.dungeon = Dungeon()
        
# The A* algorithm terminates once it finds the shortest path to a specified goal, rather than
# generating the entire shortest-path tree from a specified source to all possible goals.
