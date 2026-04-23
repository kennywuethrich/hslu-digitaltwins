"""Utility functions for the glucose-insulin digital twin.

Provides unit conversions and simple physiological helper functions
used across the model and simulation modules.
"""

import numpy as np


def meal_glucose_rate(
    time_min: float,
    total_glucose_mmol: float,
    absorption_rate_min: float = 30.0,
) -> float:
    """Model the glucose appearance rate from a meal as an exponential.

    Uses a simple first-order absorption model:
        Ra(t) = (D / tau) * exp(-t / tau)

    where D is the total glucose dose and tau the absorption time constant.

    Args:
        time_min: Time since meal ingestion [min]. Must be >= 0.
        total_glucose_mmol: Total glucose content of the meal [mmol].
        absorption_rate_min: Absorption time constant tau [min].
            Defaults to 30.

    Returns:
        Glucose appearance rate [mmol/min] at *time_min*.

    Raises:
        ValueError: If *total_glucose_mmol* or *absorption_rate_min*
            are not strictly positive.
    """
    if total_glucose_mmol <= 0:
        raise ValueError(
            f"total_glucose_mmol must be positive, got {total_glucose_mmol}"
        )
    if absorption_rate_min <= 0:
        raise ValueError(
            f"absorption_rate_min must be positive, got {absorption_rate_min}"
        )

    tau = absorption_rate_min
    return float((total_glucose_mmol / tau) * np.exp(-time_min / tau))


def mmol_per_l_to_mg_per_dl(value_mmol_l: float) -> float:
    """Convert blood glucose from mmol/L to mg/dL.

    Args:
        value_mmol_l: Glucose concentration [mmol/L].

    Returns:
        Glucose concentration [mg/dL].
    """
    return value_mmol_l * 18.0182


def mg_per_dl_to_mmol_per_l(value_mg_dl: float) -> float:
    """Convert blood glucose from mg/dL to mmol/L.

    Args:
        value_mg_dl: Glucose concentration [mg/dL].

    Returns:
        Glucose concentration [mmol/L].
    """
    return value_mg_dl / 18.0182
