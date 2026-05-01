"""Direktes Modell für Insulinentscheidungen aus CGM-Daten.

Das Modul enthält kein physiologisches ODE-Modell mehr. Es nimmt die
gemessene Glukose-Zeitreihe als Eingang und berechnet daraus direkt
eine Insulin-Zeitreihe auf Basis von Glukose, erster und zweiter
Ableitung sowie einer kurzen Vorhersage.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
from numpy.typing import NDArray

PatientProfile = Callable[[float], float]


@dataclass
class GlucoseInsulinModel:
    """Einfache CGM-zu-Insulin-Policy.

    Die Klasse hält nur die minimale Historie, die für Ableitung und
    Kurzvorhersage nötig ist.
    """

    target_mmol_l: float = 6.0
    kp: float = 0.1
    max_rate: float = 5.0
    hypo_block: float = 3.5
    alert_threshold: float = 8.5
    use_prediction: bool = True
    prediction_horizon_min: float = 15.0
    patient_profile: PatientProfile | None = None

    _last_time: Optional[float] = None
    _last_glucose: Optional[float] = None
    _last_g1: Optional[float] = None

    def __call__(self, time_min: float, glucose_mmol_l: float) -> float:
        """Berechnet die Insulinrate für einen Zeitpunkt.

        Args:
            time_min: Zeit [min].
            glucose_mmol_l: Gemessene Glukose [mmol/L].

        Returns:
            Insulinrate [pmol/L/min].
        """
        glucose_cgm = float(glucose_mmol_l)
        patient_rate = 0.0
        if self.patient_profile is not None:
            patient_rate = float(self.patient_profile(time_min))
            if patient_rate > 0.0:
                self._last_time = float(time_min)
                self._last_glucose = glucose_cgm
                self._last_g1 = None
                return patient_rate

        g1 = 0.0
        g2 = 0.0
        if self._last_time is not None and self._last_glucose is not None:
            dt = float(time_min - self._last_time)
            if dt > 0.0:
                g1 = (glucose_cgm - self._last_glucose) / dt
                if self._last_g1 is not None:
                    g2 = (g1 - self._last_g1) / dt

        self._last_time = float(time_min)
        self._last_glucose = glucose_cgm
        self._last_g1 = g1

        glucose_for_decision = glucose_cgm
        if self.use_prediction:
            horizon = float(self.prediction_horizon_min)
            glucose_for_decision = (
                glucose_cgm + g1 * horizon + 0.5 * g2 * horizon * horizon
            )

        if glucose_for_decision < self.hypo_block:
            return 0.0

        threshold = (
            self.target_mmol_l
            if self.patient_profile is None
            else self.alert_threshold
        )
        error = glucose_for_decision - threshold
        if error <= 0.0:
            return 0.0

        rate = self.kp * error
        return float(min(rate, self.max_rate))

    def build_profile(
        self,
        time_min: NDArray[np.float64],
        glucose_mmol_l: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """Berechnet eine vollständige Insulin-Zeitreihe.

        Args:
            time_min: Zeitvektor [min].
            glucose_mmol_l: Glukosewerte [mmol/L].

        Returns:
            Insulinzeitreihe [pmol/L/min].
        """
        if time_min.shape != glucose_mmol_l.shape:
            raise ValueError(
                "time_min and glucose_mmol_l must have same shape"
            )

        self._last_time = None
        self._last_glucose = None
        self._last_g1 = None

        insulin_rate = np.zeros_like(glucose_mmol_l, dtype=np.float64)
        for index, (current_time, current_glucose) in enumerate(
            zip(time_min, glucose_mmol_l, strict=True)
        ):
            insulin_rate[index] = self(
                float(current_time), float(current_glucose)
            )
        return insulin_rate
