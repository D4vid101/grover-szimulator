"""Build a self-contained browser demo from the Python simulation."""

import json
from pathlib import Path

from grover import optimal_iterations, simulate


def main():
    root = Path(__file__).resolve().parent
    datasets = {}
    for qubits in range(1, 9):
        size = 1 << qubits
        # Unmarked states share one amplitude, so the same trajectory works
        # for any target index. The browser only chooses which bar to mark.
        datasets[qubits] = {
            "recommended": optimal_iterations(size),
            "steps": [
                [step.operation, step.iteration, step.amplitudes[1],
                 step.amplitudes[0], *step.coordinates]
                for step in simulate(qubits, target=0, iterations=40)
            ],
        }
    template = (root / "browser-template.html").read_text(encoding="utf-8")
    output = root / "GroverSzimulator.html"
    output.write_text(template.replace("__GROVER_DATA__", json.dumps(datasets)), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
