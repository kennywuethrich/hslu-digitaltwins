"""Glucose-Insulin Digital Twin package.

This package implements a low-order grey-box compartment model of the
human glucose-insulin system, following the E-DES modelling approach.

Typical usage example::

    from glucose_insulin.model import GlucoseInsulinModel
    from glucose_insulin.simulation import run_simulation

    model = GlucoseInsulinModel()
    result = run_simulation(model, meal_glucose_mmol=50.0, duration_min=240)
"""

from glucose_insulin.model import GlucoseInsulinModel
from glucose_insulin.simulation import SimulationResult, run_simulation

__all__ = ["GlucoseInsulinModel", "SimulationResult", "run_simulation"]
