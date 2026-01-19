import unittest
from bowyer_watson import BowyerWatson

class TestBowyerWatson(unittest.TestCase):
    def setUp(self):
        self.empty_bw = BowyerWatson([])

    def test_empty_bw(self):
        self.assertEqual(len(self.empty_bw.points), 0)