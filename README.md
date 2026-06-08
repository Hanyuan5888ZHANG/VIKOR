# VIKOR

This repository contains a simple Python implementation of **VIKOR** for
multi-criteria decision making.

The main file is [VIKOR.py](models/VIKOR.py), which provides reusable functions
for ranking alternatives and identifying compromise solutions when several
criteria conflict with each other.

VIKOR stands for *VIseKriterijumska Optimizacija I Kompromisno Resenje*, which is
usually translated as **multi-criteria optimization and compromise solution**.
The method is especially useful when a decision maker wants an alternative that is
close to the ideal solution while balancing group utility and individual regret.

## Files

- [VIKOR.py](models/VIKOR.py): reusable Python implementation.
- [test.py](test.py): small runnable example.
- [tests/test_vikor.py](tests/test_vikor.py): unit tests for ranking,
  validation, and edge cases.

## Requirements

- Python 3.9+

The implementation uses only the Python standard library, so no third-party
packages are required.

## Principle

Assume there are `m` alternatives and `n` criteria. The decision matrix contains
the performance value of each alternative on each criterion.

VIKOR follows these main steps:

1. Define the best and worst value for each criterion.
   - For a benefit criterion, the best value is the maximum and the worst value is
     the minimum.
   - For a cost criterion, the best value is the minimum and the worst value is
     the maximum.

2. Calculate the weighted normalized loss for each alternative and criterion.
   This measures how far an alternative is from the best value on each criterion.

3. Calculate `S`, the overall group utility loss:

   ```text
   S_i = sum_j loss_ij
   ```

4. Calculate `R`, the maximum individual regret:

   ```text
   R_i = max_j loss_ij
   ```

5. Calculate `Q`, the VIKOR index:

   ```text
   Q_i = v * (S_i - S*) / (S- - S*) + (1 - v) * (R_i - R*) / (R- - R*)
   ```

   where:

   - `S*` is the minimum `S`.
   - `S-` is the maximum `S`.
   - `R*` is the minimum `R`.
   - `R-` is the maximum `R`.
   - `v` is the decision strategy weight, usually `0.5`.

The alternatives are ranked in ascending order of `Q`. A smaller `Q` means a
better compromise according to VIKOR.

## Compromise Solution

VIKOR does not only rank alternatives. It also checks whether the best-ranked
alternative can be accepted as a compromise solution.

The method checks two conditions:

1. **Acceptable advantage**

   ```text
   Q(A2) - Q(A1) >= 1 / (m - 1)
   ```

   where `A1` is the best-ranked alternative and `A2` is the second-best-ranked
   alternative.

2. **Acceptable stability**

   The best-ranked alternative by `Q` should also be ranked first by `S` or `R`.

If both conditions hold, the best `Q` alternative is the compromise solution.
If one condition fails, VIKOR returns a compromise set instead of only one
alternative.

## Example

Run:

```bash
python3 test.py
```

Example usage:

```python
from models.VIKOR import vikor

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

for result in analysis.results:
    print(result)

print("Compromise solution:", analysis.compromise_solutions)
```

## Code Explanation

The `vikor` function performs the complete method:

1. `_validate_inputs` checks matrix shape, numeric values, weights, criteria
   directions, alternative names, and the `v` parameter.
2. `_normalize_weights` converts any positive weight scale into weights that sum
   to `1`.
3. `_best_and_worst_values` finds the ideal and anti-ideal value for every
   criterion.
4. `_weighted_losses` calculates the normalized weighted distance from the ideal
   value.
5. `_rank_results` calculates `S`, `R`, and `Q`, then sorts alternatives from best
   to worst.
6. `_compromise_solutions` applies the acceptable advantage and acceptable
   stability tests.

This implementation is designed to be easy to read and teach, so the major VIKOR
steps are kept in separate helper functions.

## References

- Opricovic, S. (1998). *Multicriteria Optimization of Civil Engineering
  Systems*. Faculty of Civil Engineering, Belgrade.
- Opricovic, S., & Tzeng, G.-H. (2004). Compromise solution by MCDM methods: A
  comparative analysis of VIKOR and TOPSIS. *European Journal of Operational
  Research*, 156(2), 445-455.

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for the
full text.
