"""VIKOR method for multi-criteria decision making.

The VIKOR method ranks alternatives and identifies a compromise solution by
combining group utility loss (S), individual regret (R), and the VIKOR index (Q).
Lower Q values represent better compromise alternatives.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, List, Sequence, Tuple


CriterionDirection = str


@dataclass(frozen=True)
class VIKORResult:
    """Ranking result for one alternative."""

    alternative: str
    s: float
    r: float
    q: float
    rank: int


@dataclass(frozen=True)
class VIKORAnalysis:
    """Complete VIKOR analysis output."""

    results: List[VIKORResult]
    best_values: List[float]
    worst_values: List[float]
    compromise_solutions: List[str]
    acceptable_advantage: bool
    acceptable_stability: bool


def vikor(
    matrix: Sequence[Sequence[float]],
    weights: Sequence[float],
    criteria: Sequence[CriterionDirection],
    alternatives: Sequence[str] | None = None,
    v: float = 0.5,
) -> VIKORAnalysis:
    """Rank alternatives with the VIKOR method.

    Args:
        matrix: Decision matrix where each row is an alternative and each column
            is a criterion.
        weights: Criterion weights. They do not need to sum to 1 because the
            function normalizes them automatically.
        criteria: Criterion directions. Use "benefit" or "cost". The aliases
            "max" and "min" are also accepted.
        alternatives: Optional alternative names. If omitted, names are generated
            as A1, A2, and so on.
        v: Strategy weight in the Q index. A larger value gives more importance
            to group utility S, while a smaller value gives more importance to
            individual regret R. The common default is 0.5.

    Returns:
        A VIKORAnalysis object containing ranked results and compromise
        solutions.
    """

    clean_matrix, clean_weights, clean_criteria, clean_alternatives = _validate_inputs(
        matrix, weights, criteria, alternatives, v
    )
    normalized_weights = _normalize_weights(clean_weights)
    best_values, worst_values = _best_and_worst_values(clean_matrix, clean_criteria)
    losses = _weighted_losses(
        clean_matrix, normalized_weights, clean_criteria, best_values, worst_values
    )
    ranked_results = _rank_results(losses, clean_alternatives, v)
    compromise, acceptable_advantage, acceptable_stability = _compromise_solutions(
        ranked_results
    )

    return VIKORAnalysis(
        results=ranked_results,
        best_values=best_values,
        worst_values=worst_values,
        compromise_solutions=compromise,
        acceptable_advantage=acceptable_advantage,
        acceptable_stability=acceptable_stability,
    )


def _validate_inputs(
    matrix: Sequence[Sequence[float]],
    weights: Sequence[float],
    criteria: Sequence[CriterionDirection],
    alternatives: Sequence[str] | None,
    v: float,
) -> Tuple[List[List[float]], List[float], List[str], List[str]]:
    if not 0 <= v <= 1:
        raise ValueError("v must be between 0 and 1.")

    if not matrix:
        raise ValueError("matrix must contain at least one alternative.")

    clean_matrix: List[List[float]] = []
    row_length = len(matrix[0])
    if row_length == 0:
        raise ValueError("matrix must contain at least one criterion.")

    for row_index, row in enumerate(matrix):
        if len(row) != row_length:
            raise ValueError("all rows in matrix must have the same length.")

        clean_row = []
        for column_index, value in enumerate(row):
            try:
                number = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"matrix[{row_index}][{column_index}] must be numeric."
                ) from exc
            if not isfinite(number):
                raise ValueError(
                    f"matrix[{row_index}][{column_index}] must be finite."
                )
            clean_row.append(number)
        clean_matrix.append(clean_row)

    if len(weights) != row_length:
        raise ValueError("weights length must match the number of criteria.")

    clean_weights = []
    for index, weight in enumerate(weights):
        try:
            number = float(weight)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"weights[{index}] must be numeric.") from exc
        if not isfinite(number):
            raise ValueError(f"weights[{index}] must be finite.")
        if number < 0:
            raise ValueError("weights must be non-negative.")
        clean_weights.append(number)

    if sum(clean_weights) <= 0:
        raise ValueError("at least one weight must be greater than zero.")

    if len(criteria) != row_length:
        raise ValueError("criteria length must match the number of criteria.")

    clean_criteria = []
    for index, criterion in enumerate(criteria):
        normalized = str(criterion).strip().lower()
        if normalized == "max":
            normalized = "benefit"
        elif normalized == "min":
            normalized = "cost"

        if normalized not in {"benefit", "cost"}:
            raise ValueError(
                f"criteria[{index}] must be 'benefit', 'cost', 'max', or 'min'."
            )
        clean_criteria.append(normalized)

    if alternatives is None:
        clean_alternatives = [f"A{index + 1}" for index in range(len(clean_matrix))]
    else:
        if len(alternatives) != len(clean_matrix):
            raise ValueError("alternatives length must match the number of rows.")
        clean_alternatives = [str(alternative) for alternative in alternatives]
        if len(set(clean_alternatives)) != len(clean_alternatives):
            raise ValueError("alternative names must be unique.")

    return clean_matrix, clean_weights, clean_criteria, clean_alternatives


def _normalize_weights(weights: Sequence[float]) -> List[float]:
    total = sum(weights)
    return [weight / total for weight in weights]


def _best_and_worst_values(
    matrix: Sequence[Sequence[float]], criteria: Sequence[str]
) -> Tuple[List[float], List[float]]:
    best_values = []
    worst_values = []

    for column_index, criterion in enumerate(criteria):
        column = [row[column_index] for row in matrix]
        if criterion == "benefit":
            best_values.append(max(column))
            worst_values.append(min(column))
        else:
            best_values.append(min(column))
            worst_values.append(max(column))

    return best_values, worst_values


def _weighted_losses(
    matrix: Sequence[Sequence[float]],
    weights: Sequence[float],
    criteria: Sequence[str],
    best_values: Sequence[float],
    worst_values: Sequence[float],
) -> List[List[float]]:
    losses = []

    for row in matrix:
        row_losses = []
        for column_index, value in enumerate(row):
            best = best_values[column_index]
            worst = worst_values[column_index]
            denominator = abs(best - worst)

            if denominator == 0:
                normalized_loss = 0.0
            elif criteria[column_index] == "benefit":
                normalized_loss = (best - value) / denominator
            else:
                normalized_loss = (value - best) / denominator

            row_losses.append(weights[column_index] * normalized_loss)
        losses.append(row_losses)

    return losses


def _rank_results(
    losses: Sequence[Sequence[float]], alternatives: Sequence[str], v: float
) -> List[VIKORResult]:
    s_values = [sum(row) for row in losses]
    r_values = [max(row) if row else 0.0 for row in losses]

    s_min, s_max = min(s_values), max(s_values)
    r_min, r_max = min(r_values), max(r_values)

    q_values = []
    for s_value, r_value in zip(s_values, r_values):
        s_term = 0.0 if s_max == s_min else (s_value - s_min) / (s_max - s_min)
        r_term = 0.0 if r_max == r_min else (r_value - r_min) / (r_max - r_min)
        q_values.append(v * s_term + (1 - v) * r_term)

    indexed_results = [
        (index, alternatives[index], s_values[index], r_values[index], q_values[index])
        for index in range(len(alternatives))
    ]
    indexed_results.sort(key=lambda item: (item[4], item[2], item[3], item[0]))

    return [
        VIKORResult(
            alternative=alternative,
            s=s_value,
            r=r_value,
            q=q_value,
            rank=rank,
        )
        for rank, (_, alternative, s_value, r_value, q_value) in enumerate(
            indexed_results, start=1
        )
    ]


def _compromise_solutions(results: Sequence[VIKORResult]) -> Tuple[List[str], bool, bool]:
    if len(results) == 1:
        return [results[0].alternative], True, True

    dq = 1 / (len(results) - 1)
    best = results[0]
    second_best = results[1]

    acceptable_advantage = (second_best.q - best.q) >= dq
    best_by_s = min(results, key=lambda result: (result.s, result.q, result.rank))
    best_by_r = min(results, key=lambda result: (result.r, result.q, result.rank))
    acceptable_stability = best.alternative in {
        best_by_s.alternative,
        best_by_r.alternative,
    }

    if acceptable_advantage and acceptable_stability:
        return [best.alternative], True, True

    if not acceptable_advantage:
        compromise = [
            result.alternative for result in results if (result.q - best.q) < dq
        ]
        return compromise, False, acceptable_stability

    return [best.alternative, second_best.alternative], True, False


def print_vikor_table(results: Iterable[VIKORResult]) -> None:
    """Print a compact VIKOR result table."""

    print(f"{'Rank':>4}  {'Alternative':<12}  {'S':>10}  {'R':>10}  {'Q':>10}")
    print("-" * 52)
    for result in results:
        print(
            f"{result.rank:>4}  {result.alternative:<12}  "
            f"{result.s:>10.4f}  {result.r:>10.4f}  {result.q:>10.4f}"
        )
