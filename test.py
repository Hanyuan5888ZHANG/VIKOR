"""Example usage of the VIKOR implementation."""

from models.VIKOR import print_vikor_table, vikor


def main() -> None:
    matrix = [
        [25000, 7, 10, 6],
        [27000, 8, 7, 8],
        [24000, 6, 12, 5],
        [26000, 9, 8, 7],
    ]

    weights = [0.35, 0.30, 0.20, 0.15]
    criteria = ["cost", "benefit", "cost", "benefit"]
    alternatives = ["A1", "A2", "A3", "A4"]

    analysis = vikor(matrix, weights, criteria, alternatives, v=0.5)

    print_vikor_table(analysis.results)
    print()
    print("Best values:", analysis.best_values)
    print("Worst values:", analysis.worst_values)
    print("Acceptable advantage:", analysis.acceptable_advantage)
    print("Acceptable stability:", analysis.acceptable_stability)
    print("Compromise solution(s):", ", ".join(analysis.compromise_solutions))


if __name__ == "__main__":
    main()
