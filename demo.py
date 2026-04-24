"""Einfache Demo für das T1D-Basismodell.

Start:
    python demo.py
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from glucose_insulin.model import GlucoseInsulinModel, ModelParameters
from glucose_insulin.plotting import plot_simulation
from glucose_insulin.simulation import (
    InputProfiles,
    SimulationConfig,
    run_simulation,
)
from glucose_insulin.utils import rectangular_pulse


def main() -> None:
    """Startet eine alltagsnahe Beispielsimulation."""
    model = GlucoseInsulinModel(
        parameters=ModelParameters(
            glucose_basal=5.0,
            insulin_basal=10.0,
            k1=0.01,
            k2=0.0005,
            k3=0.5,
            k4=0.05,
        )
    )

    def activity_rate(time_min: float) -> float:
        return rectangular_pulse(
            time_min=time_min,
            start_min=90.0,
            end_min=130.0,
            height=0.12,
        )

    def exogenous_insulin_rate(time_min: float) -> float:
        return rectangular_pulse(
            time_min=time_min,
            start_min=5.0,
            end_min=20.0,
            height=0.08,
        )

    result = run_simulation(
        model=model,
        config=SimulationConfig(
            meal_glucose_mmol=65.0,
            duration_min=240.0,
            absorption_rate_min=30.0,
            n_points=500,
        ),
        profiles=InputProfiles(
            activity_rate_fn=activity_rate,
            exogenous_insulin_rate_fn=exogenous_insulin_rate,
        ),
    )
    plot_simulation(result)


if __name__ == "__main__":
    main()
