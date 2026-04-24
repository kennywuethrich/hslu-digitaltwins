"""Hilfsfunktionen für den Glukose-Insulin-Digital-Twin.

Enthält Umrechnungen und einfache Eingangsprofile für Mahlzeiten,
Aktivität und Insulinabgaben.
"""

import numpy as np


def meal_glucose_rate(
    time_min: float,
    total_glucose_mmol: float,
    absorption_rate_min: float = 30.0,
) -> float:
    """Modelliert die Glukoseaufnahme aus einer Mahlzeit exponentiell.

    Verwendet ein einfaches Absorptionsmodell 1. Ordnung:
        Ra(t) = (D / tau) * exp(-t / tau)

    mit D als Gesamtdosis und tau als Zeitkonstante.

    Args:
        time_min: Zeit seit Mahlzeit [min]. Muss >= 0 sein.
        total_glucose_mmol: Gesamte Glukosemenge der Mahlzeit [mmol].
        absorption_rate_min: Absorptionszeitkonstante tau [min].

    Returns:
        Glukoseeintragsrate [mmol/min] zum Zeitpunkt *time_min*.

    Raises:
        ValueError: Falls Eingaben unplausibel sind.
    """
    if time_min < 0:
        raise ValueError(f"time_min must be >= 0, got {time_min}")
    if total_glucose_mmol < 0:
        raise ValueError(
            "total_glucose_mmol must be >= 0, " f"got {total_glucose_mmol}"
        )
    if absorption_rate_min <= 0:
        raise ValueError(
            f"absorption_rate_min must be positive, got {absorption_rate_min}"
        )

    tau = absorption_rate_min
    return float((total_glucose_mmol / tau) * np.exp(-time_min / tau))


def mmol_per_l_to_mg_per_dl(value_mmol_l: float) -> float:
    """Konvertiert Blutglukose von mmol/L nach mg/dL.

    Args:
        value_mmol_l: Glucose concentration [mmol/L].

    Returns:
        Glucose concentration [mg/dL].
    """
    return value_mmol_l * 18.0182


def mg_per_dl_to_mmol_per_l(value_mg_dl: float) -> float:
    """Konvertiert Blutglukose von mg/dL nach mmol/L.

    Args:
        value_mg_dl: Glucose concentration [mg/dL].

    Returns:
        Glucose concentration [mmol/L].
    """
    return value_mg_dl / 18.0182


def rectangular_pulse(
    time_min: float,
    start_min: float,
    end_min: float,
    height: float,
) -> float:
    """Gibt ein rechteckiges Eingangsprofil zurück.

    Das Profil ist zwischen *start_min* und *end_min* konstant *height*.
    Außerhalb dieses Intervalls ist der Wert null.

    Args:
        time_min: Aktuelle Zeit [min].
        start_min: Startzeit [min].
        end_min: Endzeit [min]. Muss > start_min sein.
        height: Höhe des Pulses in der jeweiligen Eingangs-Einheit.

    Returns:
        Profilwert zum Zeitpunkt *time_min*.

    Raises:
        ValueError: Falls *end_min* <= *start_min*.
    """
    if end_min <= start_min:
        raise ValueError(
            f"end_min must be > start_min, got {end_min} <= {start_min}"
        )
    if start_min <= time_min <= end_min:
        return height
    return 0.0
