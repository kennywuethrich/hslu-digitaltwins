"""Compartment model of the glucose-insulin system.

This module defines the E-DES-inspired grey-box ODE model for the
glucose-insulin system. The model captures the effect of a meal on
blood plasma glucose and insulin concentrations.

System overview:
    Input:  meal glucose equivalent [mmol]
    States: plasma glucose, plasma insulin, interstitial glucose
    Output: interstitial glucose [mmol/L]  (CGM measurement)

Note:
    Model equations are placeholders pending SW02 model specification.
    Do NOT add equations before the specification is finalised.
"""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray


@dataclass
class ModelParameters:
    """Parameters for the glucose-insulin compartment model.

    All parameters are placeholders; values will be identified during
    the model specification and parameter estimation phases.

    Attributes:
        glucose_distribution_volume: Volume of the glucose distribution
            compartment [L].
        insulin_distribution_volume: Volume of the insulin distribution
            compartment [L].
        glucose_basal: Basal plasma glucose concentration [mmol/L].
        insulin_basal: Basal plasma insulin concentration [pmol/L].
    """

    glucose_distribution_volume: float = 1.0  # [L]       – to be identified
    insulin_distribution_volume: float = 1.0  # [L]       – to be identified
    glucose_basal: float = 5.0  # [mmol/L]   – typical fasting
    insulin_basal: float = 60.0  # [pmol/L]   – typical fasting


@dataclass
class GlucoseInsulinModel:
    """Grey-box compartment model of the glucose-insulin system.

    Implements the ODE right-hand side for numerical integration.
    The model will be extended incrementally throughout the semester.

    Attributes:
        parameters: Physiological and model parameters.
    """

    parameters: ModelParameters = field(default_factory=ModelParameters)

    def initial_state(self) -> NDArray[np.float64]:
        """Return the initial state vector at basal equilibrium.

        Returns:
            Array of shape (3,) with:
                [0] plasma glucose    [mmol/L]
                [1] plasma insulin    [pmol/L]
                [2] interstitial glucose [mmol/L]
        """
        p = self.parameters
        return np.array(
            [p.glucose_basal, p.insulin_basal, p.glucose_basal],
            dtype=np.float64,
        )

    def odes(
        self,
        _time: float,
        state: NDArray[np.float64],
        meal_rate: float,
    ) -> NDArray[np.float64]:
        """Compute the ODE right-hand side (dx/dt).

        Args:
            _time: Current simulation time [min]. Unused directly; kept
                for compatibility with scipy ODE solvers.
            state: Current state vector [plasma_glucose, plasma_insulin,
                interstitial_glucose].
            meal_rate: Glucose appearance rate from meal [mmol/min].

        Returns:
            Derivative vector dx/dt of the same shape as *state*.

        Note:
            Equations are intentionally left as zeros until the model
            specification (SW02) is complete.
        """
        # TODO (SW02): Replace with derived model equations.
        _ = state
        _ = meal_rate
        return np.zeros(3, dtype=np.float64)

    def cgm_output(self, state: NDArray[np.float64]) -> float:
        """Return the CGM (interstitial glucose) measurement.

        Args:
            state: Current state vector.

        Returns:
            Interstitial glucose concentration [mmol/L].
        """
        return float(state[2])
