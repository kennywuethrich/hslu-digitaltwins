"""Einfache Demo für das T1D-Basismodell.

Start:
    python demo.py
"""

from bootstrap import add_src_to_path

add_src_to_path()

from config.scenarios import (
    DEFAULT_SCENARIO,
    build_runtime,
    preset_values,
)
from glucose_insulin.model import GlucoseInsulinModel
from glucose_insulin.plotting import plot_simulation
from glucose_insulin.simulation import run_simulation


def main() -> None:
    """Startet eine alltagsnahe Beispielsimulation."""
    values = preset_values(DEFAULT_SCENARIO)
    runtime = build_runtime(values, n_points=500)

    model = GlucoseInsulinModel(parameters=runtime.model_parameters)

    result = run_simulation(
        model=model,
        config=runtime.simulation_config,
        profiles=runtime.input_profiles,
    )
    plot_simulation(result)


if __name__ == "__main__":
    main()
