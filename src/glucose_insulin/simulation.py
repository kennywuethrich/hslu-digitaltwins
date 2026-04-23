"""Simulation runner for the glucose-insulin digital twin.

Provides a high-level interface to integrate the ODE model over a
specified time horizon and collect results in a structured dataclass.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp  # type: ignore[import-untyped]

from glucose_insulin.model import GlucoseInsulinModel
from glucose_insulin.utils import meal_glucose_rate


@dataclass
class SimulationResult:
    """Container for a completed simulation run.

    Attributes:
        time_min: Time vector [min], shape (N,).
        plasma_glucose: Plasma glucose trajectory [mmol/L], shape (N,).
        plasma_insulin: Plasma insulin trajectory [pmol/L], shape (N,).
        cgm_glucose: Interstitial glucose (CGM output) [mmol/L], shape (N,).
    """

    time_min: NDArray[np.float64]
    plasma_glucose: NDArray[np.float64]
    plasma_insulin: NDArray[np.float64]
    cgm_glucose: NDArray[np.float64]


def run_simulation(
    model: GlucoseInsulinModel,
    meal_glucose_mmol: float,
    duration_min: float = 240.0,
    absorption_rate_min: float = 30.0,
    n_points: int = 500,
) -> SimulationResult:
    """Integrate the glucose-insulin model over a meal scenario.

    Args:
        model: Configured GlucoseInsulinModel instance.
        meal_glucose_mmol: Total glucose content of the meal [mmol].
        duration_min: Simulation duration [min]. Defaults to 240.
        absorption_rate_min: Time constant for meal absorption [min].
            Defaults to 30.
        n_points: Number of output time points. Defaults to 500.

    Returns:
        SimulationResult with time and state trajectories.

    Raises:
        RuntimeError: If the ODE solver does not converge.
    """
    t_span = (0.0, duration_min)
    t_eval = np.linspace(0.0, duration_min, n_points)
    x0 = model.initial_state()

    def rhs(t: float, x: NDArray[np.float64]) -> NDArray[np.float64]:
        rate = meal_glucose_rate(
            time_min=t,
            total_glucose_mmol=meal_glucose_mmol,
            absorption_rate_min=absorption_rate_min,
        )
        return model.odes(t, x, meal_rate=rate)

    solution = solve_ivp(
        rhs,
        t_span,
        x0,
        method="RK45",
        t_eval=t_eval,
        rtol=1e-6,
        atol=1e-8,
    )

    if not solution.success:
        raise RuntimeError(f"ODE solver failed: {solution.message}")

    return SimulationResult(
        time_min=solution.t,
        plasma_glucose=solution.y[0],
        plasma_insulin=solution.y[1],
        cgm_glucose=solution.y[2],
    )
