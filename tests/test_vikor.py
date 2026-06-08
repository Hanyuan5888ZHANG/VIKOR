import unittest

from models.VIKOR import vikor


class VIKORTestCase(unittest.TestCase):
    def test_ranks_example_from_readme(self):
        matrix = [
            [25000, 7, 10, 6],
            [27000, 8, 7, 8],
            [24000, 6, 12, 5],
            [26000, 9, 8, 7],
        ]
        weights = [0.35, 0.30, 0.20, 0.15]
        criteria = ["cost", "benefit", "cost", "benefit"]
        alternatives = ["A1", "A2", "A3", "A4"]

        analysis = vikor(matrix, weights, criteria, alternatives)
        ranking = [result.alternative for result in analysis.results]

        self.assertEqual(ranking, ["A4", "A1", "A2", "A3"])
        self.assertEqual(analysis.compromise_solutions, ["A4", "A1"])
        self.assertFalse(analysis.acceptable_advantage)
        self.assertTrue(analysis.acceptable_stability)

    def test_weight_scale_is_normalized(self):
        matrix = [
            [10, 80],
            [12, 95],
            [8, 70],
        ]
        criteria = ["cost", "benefit"]

        analysis_a = vikor(matrix, [0.4, 0.6], criteria)
        analysis_b = vikor(matrix, [4, 6], criteria)

        self.assertEqual(
            [result.alternative for result in analysis_a.results],
            [result.alternative for result in analysis_b.results],
        )
        for result_a, result_b in zip(analysis_a.results, analysis_b.results):
            self.assertAlmostEqual(result_a.q, result_b.q)

    def test_accepts_min_max_aliases(self):
        matrix = [
            [5, 100],
            [3, 80],
        ]

        analysis = vikor(matrix, [1, 1], ["min", "max"], ["A", "B"])

        self.assertEqual(analysis.results[0].alternative, "A")

    def test_identical_criterion_values_do_not_divide_by_zero(self):
        matrix = [
            [10, 3],
            [10, 5],
            [10, 4],
        ]

        analysis = vikor(matrix, [0.5, 0.5], ["cost", "benefit"])

        self.assertEqual(analysis.best_values, [10.0, 5.0])
        self.assertEqual(analysis.worst_values, [10.0, 3.0])
        self.assertEqual(analysis.results[0].alternative, "A2")

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            vikor([], [1], ["benefit"])

        with self.assertRaises(ValueError):
            vikor([[1, 2], [3]], [1, 1], ["benefit", "cost"])

        with self.assertRaises(ValueError):
            vikor([[1, 2]], [1], ["benefit", "cost"])

        with self.assertRaises(ValueError):
            vikor([[1, 2]], [0, 0], ["benefit", "cost"])

        with self.assertRaises(ValueError):
            vikor([[1, 2]], [1, 1], ["benefit", "unknown"])

        with self.assertRaises(ValueError):
            vikor([[1, 2]], [1, 1], ["benefit", "cost"], v=1.5)


if __name__ == "__main__":
    unittest.main()
