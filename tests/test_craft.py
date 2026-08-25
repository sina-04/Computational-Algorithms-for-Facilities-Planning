import unittest

from craft import compute_cost, craft_local_search, delta_swap


class CraftTests(unittest.TestCase):
    def setUp(self):
        self.flow = [
            [0.0, 8.0, 1.0],
            [8.0, 0.0, 5.0],
            [1.0, 5.0, 0.0],
        ]
        self.distance = [
            [0.0, 10.0, 2.0],
            [10.0, 0.0, 4.0],
            [2.0, 4.0, 0.0],
        ]
        self.cost = [
            [0.0, 1.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 0.0],
        ]

    def test_swap_delta_matches_full_recalculation(self):
        original = [0, 1, 2]
        swapped = [1, 0, 2]
        delta = delta_swap(0, 1, self.flow, self.distance, self.cost, original)
        expected = compute_cost(self.flow, self.distance, self.cost, swapped)
        expected -= compute_cost(self.flow, self.distance, self.cost, original)
        self.assertAlmostEqual(delta, expected)

    def test_local_search_never_increases_cost(self):
        initial = compute_cost(self.flow, self.distance, self.cost, [0, 1, 2])
        permutation, final, history = craft_local_search(
            self.flow,
            self.distance,
            self.cost,
            ["A", "B", "C"],
        )
        self.assertCountEqual(permutation, [0, 1, 2])
        self.assertLessEqual(final, initial)
        self.assertGreaterEqual(len(history), 1)


if __name__ == "__main__":
    unittest.main()
