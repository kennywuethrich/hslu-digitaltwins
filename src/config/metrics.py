"""Zentrale Auswertung von Simulationsergebnissen."""

from dataclasses import dataclass

from glucose_insulin.simulation import SimulationResult


@dataclass
class GlucoseMetrics:
    """Kompakte Kennzahlen fuer den Glukoseverlauf.

    Attributes:
        max_glucose_mmol_l: Maximalwert der Plasma-Glukose [mmol/L].
        min_glucose_mmol_l: Minimalwert der Plasma-Glukose [mmol/L].
        end_glucose_mmol_l: Endwert der Plasma-Glukose [mmol/L].
    """

    max_glucose_mmol_l: float
    min_glucose_mmol_l: float
    end_glucose_mmol_l: float


def glucose_metrics(result: SimulationResult) -> GlucoseMetrics:
    """Berechnet zentrale Kennzahlen aus einem Simulationsergebnis.

    Args:
        result: Ergebnis einer Simulation.

    Returns:
        GlucoseMetrics mit max/min/end der Plasma-Glukose [mmol/L].
    """
    return GlucoseMetrics(
        max_glucose_mmol_l=float(result.plasma_glucose.max()),
        min_glucose_mmol_l=float(result.plasma_glucose.min()),
        end_glucose_mmol_l=float(result.plasma_glucose[-1]),
    )
