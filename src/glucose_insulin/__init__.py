"""Glucose-Insulin Digital Twin package.

This package implements a low-order grey-box compartment model of the
human glucose-insulin system, following the E-DES modelling approach.

Typical usage example::

    from glucose_insulin.model import GlucoseInsulinModel
    from glucose_insulin.simulation import run_simulation

    model = GlucoseInsulinModel()
    result = run_simulation(model, meal_glucose_mmol=50.0, duration_min=240)
"""

from glucose_insulin.model import GlucoseInsulinModel, ModelInputs
from glucose_insulin.plotting import plot_simulation
from glucose_insulin.simulation import (
    InputProfiles,
    SimulationConfig,
    SimulationResult,
    run_simulation,
)
from glucose_insulin.utils import rectangular_pulse

__all__ = [
    "GlucoseInsulinModel",
    "ModelInputs",
    "SimulationResult",
    "SimulationConfig",
    "InputProfiles",
    "run_simulation",
    "plot_simulation",
    "rectangular_pulse",
]
