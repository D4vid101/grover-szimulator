"""Real-amplitude simulation of Grover search with one marked state."""

from dataclasses import dataclass
from math import asin, floor, fsum, pi, sqrt


@dataclass(frozen=True)
class Step:
    operation: str
    iteration: int
    amplitudes: tuple[float, ...]
    target: int

    @property
    def coordinates(self) -> tuple[float, float]:
        """Signed coefficients of the unmarked and marked unit vectors."""
        values = self.amplitudes
        marked = values[self.target]
        unmarked = fsum(values[:self.target] + values[self.target + 1:])
        return unmarked / sqrt(len(values) - 1), marked

    @property
    def probability(self) -> float:
        return self.amplitudes[self.target] ** 2


def optimal_iterations(size: int) -> int:
    theta = asin(1 / sqrt(size))
    return max(0, floor(pi / (4 * theta) + 1e-12))


def simulate(qubits: int, target: int, iterations: int) -> list[Step]:
    if not 1 <= qubits <= 8:
        raise ValueError("A qubitek száma 1 és 8 közé essen.")
    size = 1 << qubits
    if not 0 <= target < size:
        raise ValueError(f"A célállapot indexe 0 és {size - 1} közé essen.")
    if not 0 <= iterations <= 40:
        raise ValueError("Az iterációk száma 0 és 40 közé essen.")

    values = [1 / sqrt(size)] * size
    history = [Step("initial", 0, tuple(values), target)]
    for iteration in range(1, iterations + 1):
        values[target] = -values[target]
        history.append(Step("oracle", iteration, tuple(values), target))
        twice_mean = 2 * fsum(values) / size
        values = [twice_mean - value for value in values]
        history.append(Step("diffusion", iteration, tuple(values), target))
    return history
