"""Direktes Modell für Insulinentscheidungen aus CGM-Daten.

Das Modul nimmt die gemessene Glukose-Zeitreihe als Eingang und berechnet
daraus eine Insulin-Zeitreihe auf Basis von Glukose, erster und zweiter
Ableitung sowie einer kurzen Vorhersage. Zusätzlich kann der Glukoseverlauf
simuliert werden, der sich aus der berechneten Insulin-Zeitreihe ergibt.
"""

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
from numpy.typing import NDArray

PatientProfile = Callable[[float], float]


def _insulin_response_kernel(
    time_min: NDArray[np.float64],
    tau1_min: float,
    tau2_min: float,
) -> NDArray[np.float64]:
    """Biexponentielles Wirkprofil für schnell-wirkendes Insulin.

    Modelliert den Anteil des bereits wirkenden Insulins über die Zeit
    (z. B. Novorapid: Onset ~15 min, Peak ~60-90 min, Dauer ~3-4 h).

    Args:
        time_min: Zeitvektor seit Insulingabe [min], muss >= 0 sein.
        tau1_min: Erste Zeitkonstante [min].
        tau2_min: Zweite Zeitkonstante [min].

    Returns:
        Normiertes Wirkprofil im Bereich [0, 1].
    """
    profile = np.exp(-time_min / tau2_min) - np.exp(-time_min / tau1_min)
    profile = np.clip(profile, 0.0, None)
    peak = profile.max()
    if peak <= 0.0:
        return np.zeros_like(time_min)
    return profile / peak


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

    isf_mmol_per_iu: float = 0.05
    insulin_tau1_min: float = 55.0
    insulin_tau2_min: float = 70.0
    insulin_rate_to_iu: float = 0.5

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

    def simulate_glucose_with_insulin(
        self,
        time_min: NDArray[np.float64],
        glucose_measured_mmol_l: NDArray[np.float64],
        insulin_rate: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """Simuliert den Glukoseverlauf unter Wirkung der Insulin-Zeitreihe.

        An jedem Zeitpunkt wird die gesamte zurückliegende Insulingabe mit
        dem biexponentiellen Wirkprofil gefaltet. Das Ergebnis wird als
        zusätzliche glukosesenkende Wirkung von der gemessenen Zeitreihe
        abgezogen. So entsteht der Verlauf, der sich ergäbe, wenn das
        Modell-Insulin tatsächlich verabreicht würde.

        Args:
            time_min: Zeitvektor [min], gleichmäßig oder nahezu gleichmäßig.
            glucose_measured_mmol_l: Gemessene Glukose [mmol/L].
            insulin_rate: Vom Modell berechnete Rate [pmol/L/min].

        Returns:
            Simulierte Glukose-Zeitreihe [mmol/L].
        """
        if time_min.shape != glucose_measured_mmol_l.shape:
            raise ValueError(
                "time_min and glucose_measured_mmol_l must have same shape"
            )
        if time_min.shape != insulin_rate.shape:
            raise ValueError("time_min and insulin_rate must have same shape")

        if time_min.size < 2:
            return glucose_measured_mmol_l.astype(np.float64).copy()

        dt_min = float(np.median(np.diff(time_min)))
        kernel_length = int(
            round(
                6.0
                * max(self.insulin_tau1_min, self.insulin_tau2_min)
                / dt_min
            )
        )
        kernel_time = np.arange(kernel_length, dtype=np.float64) * dt_min
        kernel = _insulin_response_kernel(
            kernel_time, self.insulin_tau1_min, self.insulin_tau2_min
        )

        dose_iu_per_step = insulin_rate * self.insulin_rate_to_iu * dt_min
        insulin_effect = np.convolve(dose_iu_per_step, kernel, mode="full")[
            : time_min.size
        ]

        glucose_simulated = (
            glucose_measured_mmol_l - self.isf_mmol_per_iu * insulin_effect
        )
        return np.maximum(glucose_simulated, 2.5)
