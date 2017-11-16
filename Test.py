import unittest
from Node import Node


class TestDifficultyAdjustment(unittest.TestCase):

    def test_getAverageBlockTime(self):
        times = []
        ten_minutes_in_seconds = 10 * 60
        for time in range(0, 2016 * ten_minutes_in_seconds, ten_minutes_in_seconds):
            print(time)
            times.append(time)

        self.assertEqual(Node.getAverageBlockTime(times), ten_minutes_in_seconds)


if __name__ == '__main__':
    unittest.main()