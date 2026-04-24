"""Kompartmentmodell des Glukose-Insulin-Systems.

Dieses Modul enthält ein bewusst einfaches, gut erklärbares ODE-Modell
für einen T1D-orientierten Use-Case. Die Eingänge sind getrennt in
Mahlzeit, Aktivität sowie endogene und exogene Insulinzufuhr.

Systemüberblick:
    Eingänge:
        - meal_rate [mmol/min]
        - activity_rate [mmol/L/min]
        - endogenous_insulin_rate [pmol/L/min]
        - exogenous_insulin_rate [pmol/L/min]
    Zustände:
        - Plasma-Glukose [mmol/L]
        - Plasma-Insulin [pmol/L]
        - Interstitielle Glukose [mmol/L]
    Ausgang:
        - Interstitielle Glukose [mmol/L] (CGM)
"""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray


@dataclass
class ModelParameters:
    """Parameter des vereinfachten T1D-Modells.

    Attributes:
        glucose_basal: Basaler Glukosewert Gb [mmol/L].
        insulin_basal: Basaler Insulinwert Ib [pmol/L].
        k1: Insulinunabhängiger Glukoseabbau [1/min].
        k2: Insulineffektivität auf Glukose [1/min].
        k3: Antwortstärke von Insulin auf Glukoseabweichung [1/min].
        k4: Insulinabbaurate [1/min].
        cgm_time_constant_min: Verzögerung Plasma->CGM [min].
    """

    glucose_basal: float = 5.0
    insulin_basal: float = 10.0
    k1: float = 0.01
    k2: float = 0.0005
    k3: float = 0.5
    k4: float = 0.05
    cgm_time_constant_min: float = 12.0


@dataclass
class ModelInputs:
    """Eingangsgrößen für einen ODE-Auswertungsschritt.

    Attributes:
        meal_rate: Mahlzeitbedingter Glukoseeintrag [mmol/min].
        activity_rate: Aktivitätsbedingter Glukoseabzug [mmol/L/min].
        endogenous_insulin_rate: Endogene Insulinzufuhr [pmol/L/min].
        exogenous_insulin_rate: Exogene Insulinzufuhr [pmol/L/min].
    """

    meal_rate: float = 0.0
    activity_rate: float = 0.0
    endogenous_insulin_rate: float = 0.0
    exogenous_insulin_rate: float = 0.0


@dataclass
class GlucoseInsulinModel:
    """Vereinfachtes Grey-Box-Modell für Glukose und Insulin.

    Die Dynamik folgt der Form:

        dI/dt = k3 * (G - Gb) - k4 * (I - Ib) + I_endogen + I_exogen
        dG/dt = -k1 * (G - Gb) - k2 * (I - Ib) + Essen - Aktivität

    Zusätzlich wird ein CGM-Zustand als verzögerte Glukosemessung geführt.

    Attributes:
        parameters: Modellparameter.
    """

    parameters: ModelParameters = field(default_factory=ModelParameters)

    def initial_state(self) -> NDArray[np.float64]:
        """Gibt den Startzustand im Basalpunkt zurück.

        Returns:
            Array der Form (3,) mit:
                [0] Plasma-Glukose [mmol/L]
                [1] Plasma-Insulin [pmol/L]
                [2] Interstitielle Glukose [mmol/L]
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
        inputs: ModelInputs,
    ) -> NDArray[np.float64]:
        """Berechnet die rechte Seite der ODEs (dx/dt).

        Args:
            _time: Simulationszeit [min], für Solver-Kompatibilität.
            state: Zustandsvektor [G, I, G_interstitiell].
            inputs: Eingangsgrößen (Mahlzeit, Aktivität, Insulinraten).

        Returns:
            Ableitungsvektor [dG/dt, dI/dt, dG_interstitiell/dt].
        """
        p = self.parameters
        glucose_plasma = float(state[0])
        insulin_plasma = float(state[1])
        glucose_interstitial = float(state[2])

        d_insulin = (
            p.k3 * (glucose_plasma - p.glucose_basal)
            - p.k4 * (insulin_plasma - p.insulin_basal)
            + inputs.endogenous_insulin_rate
            + inputs.exogenous_insulin_rate
        )
        d_glucose = (
            -p.k1 * (glucose_plasma - p.glucose_basal)
            - p.k2 * (insulin_plasma - p.insulin_basal)
            + inputs.meal_rate
            - inputs.activity_rate
        )
        d_glucose_interstitial = (
            glucose_plasma - glucose_interstitial
        ) / p.cgm_time_constant_min

        return np.array(
            [d_glucose, d_insulin, d_glucose_interstitial],
            dtype=np.float64,
        )

    def cgm_output(self, state: NDArray[np.float64]) -> float:
        """Gibt die CGM-Messung (interstitielle Glukose) zurück.

        Args:
            state: Aktueller Zustandsvektor.

        Returns:
            Interstitielle Glukosekonzentration [mmol/L].
        """
        return float(state[2])
