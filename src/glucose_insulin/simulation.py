"""Simulationsmodul für den Glukose-Insulin-Digital-Twin.

Das Modul integriert das ODE-Modell über einen Zeitbereich und erlaubt
getrennte Eingangsprofile für Mahlzeit, Aktivität sowie endogene und
exogene Insulinzufuhr.
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp  # type: ignore[import-untyped]

from glucose_insulin.model import GlucoseInsulinModel, ModelInputs
from glucose_insulin.utils import meal_glucose_rate

InputProfile = Callable[[float], float]


@dataclass
class SimulationResult:
    """Container für ein abgeschlossenes Simulationsergebnis.

    Attributes:
        time_min: Zeitvektor [min], Form (N,).
        plasma_glucose: Verlauf Plasma-Glukose [mmol/L], Form (N,).
        plasma_insulin: Verlauf Plasma-Insulin [pmol/L], Form (N,).
        cgm_glucose: Verlauf CGM-Glukose [mmol/L], Form (N,).
    """

    time_min: NDArray[np.float64]
    plasma_glucose: NDArray[np.float64]
    plasma_insulin: NDArray[np.float64]
    cgm_glucose: NDArray[np.float64]


@dataclass
class SimulationConfig:
    """Konfiguration der Simulationszeit und Mahlzeit.

    Attributes:
        meal_glucose_mmol: Gesamte Mahlzeitglukose [mmol].
        duration_min: Simulationsdauer [min].
        absorption_rate_min: Absorptionszeitkonstante [min].
        n_points: Anzahl Ausgabepunkte.
    """

    meal_glucose_mmol: float = 50.0
    duration_min: float = 240.0
    absorption_rate_min: float = 30.0
    n_points: int = 500


@dataclass
class InputProfiles:
    """Optionale Zeitprofile für externe Eingänge.

    Attributes:
        activity_rate_fn: Aktivitätsprofil a(t) [mmol/L/min].
        endogenous_insulin_rate_fn: Endogenes Insulinprofil ie(t).
        exogenous_insulin_rate_fn: Exogenes Insulinprofil ix(t).
    """

    activity_rate_fn: InputProfile | None = None
    endogenous_insulin_rate_fn: InputProfile | None = None
    exogenous_insulin_rate_fn: InputProfile | None = None


def run_simulation(
    model: GlucoseInsulinModel,
    config: SimulationConfig | None = None,
    profiles: InputProfiles | None = None,
) -> SimulationResult:
    """Integriert das Modell über ein konfigurierbares Szenario.

    Args:
        model: Konfiguriertes GlucoseInsulinModel.
        config: Simulationskonfiguration.
        profiles: Optionale Profile externer Eingänge.

    Returns:
        SimulationResult mit Zeit- und Zustandsverläufen.

    Raises:
        RuntimeError: Falls der ODE-Solver nicht konvergiert.
    """

    def input_value(profile: InputProfile | None, time_min: float) -> float:
        """Liest den Wert eines Profils zum Zeitpunkt *time_min* aus."""
        if profile is None:
            return 0.0
        return float(profile(time_min))

    if config is None:
        config = SimulationConfig()
    if profiles is None:
        profiles = InputProfiles()

    t_span = (0.0, config.duration_min)
    t_eval = np.linspace(0.0, config.duration_min, config.n_points)
    x0 = model.initial_state()

    def rhs(t: float, x: NDArray[np.float64]) -> NDArray[np.float64]:
        meal_rate = meal_glucose_rate(
            time_min=t,
            total_glucose_mmol=config.meal_glucose_mmol,
            absorption_rate_min=config.absorption_rate_min,
        )
        inputs = ModelInputs(
            meal_rate=meal_rate,
            activity_rate=input_value(profiles.activity_rate_fn, t),
            endogenous_insulin_rate=input_value(
                profiles.endogenous_insulin_rate_fn,
                t,
            ),
            exogenous_insulin_rate=input_value(
                profiles.exogenous_insulin_rate_fn,
                t,
            ),
        )
        return model.odes(
            t,
            x,
            inputs=inputs,
        )

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
