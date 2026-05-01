"""Kleine Helfer zur Vorverarbeitung von CGM-Zeitreihen.

Enthält einfache Lade-, Glättungs- und Ableitungsfunktionen, die für
die Policy-Entwicklung und Visualisierung nützlich sind.
"""

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Tuple

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class CgmSeries:
    """Geladene CGM-Zeitreihe.

    Attributes:
        time_min: Zeit in Minuten ab Start.
        glucose_mmol_l: Gemessene Glukose [mmol/L].
        timestamps: Originale Zeitstempel der Messung.
    """

    time_min: NDArray[np.float64]
    glucose_mmol_l: NDArray[np.float64]
    timestamps: list[datetime]


def _resolve_column(fieldnames: list[str], candidates: tuple[str, ...]) -> str:
    """Finds the first matching column name from a list of candidates."""
    for candidate in candidates:
        if candidate in fieldnames:
            return candidate
    raise ValueError(f"Missing columns, expected one of: {candidates}")


def _parse_timestamp(raw_timestamp: str) -> datetime:
    """Parses supported timestamp formats used in the CSV files."""
    timestamp_formats = ("%d.%m.%Y %H:%M", "%d/%m/%Y %H:%M")
    for timestamp_format in timestamp_formats:
        try:
            return datetime.strptime(raw_timestamp, timestamp_format)
        except ValueError:
            continue
    raise ValueError(f"Unsupported timestamp format: {raw_timestamp}")


def load_cgm_series(csv_path: str | Path) -> CgmSeries:
    """Lädt die CGM-Zeitreihe aus der CSV-Datei.

    Args:
        csv_path: Pfad zur CSV-Datei.

    Returns:
        Geladene Zeitreihe mit Minutenachse und Glukosewerten.

    Raises:
        ValueError: Wenn keine unterstützte Zeit- oder Glukosespalte
            gefunden wird oder keine Werte enthalten sind.
    """
    path = Path(csv_path)
    glucose_values: list[float] = []
    time_stamps: list[datetime] = []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or []
        glucose_column = _resolve_column(
            fieldnames,
            ("gluc_mmol_L", "value"),
        )
        timestamp_column = _resolve_column(
            fieldnames,
            ("timestamp", "bg_ts"),
        )
        for row in reader:
            raw_value = row.get(glucose_column, "")
            raw_timestamp = row.get(timestamp_column, "")
            if raw_value == "":
                continue
            if raw_timestamp == "":
                continue
            glucose_values.append(float(raw_value))
            time_stamps.append(_parse_timestamp(raw_timestamp))

    if not glucose_values:
        raise ValueError(f"No glucose values found in {path}")

    start_time = time_stamps[0]
    time_min = np.array(
        [(stamp - start_time).total_seconds() / 60.0 for stamp in time_stamps],
        dtype=np.float64,
    )
    glucose_mmol_l = np.asarray(glucose_values, dtype=np.float64)
    return CgmSeries(
        time_min=time_min,
        glucose_mmol_l=glucose_mmol_l,
        timestamps=time_stamps,
    )


def moving_average(
    data: NDArray[np.float64], window: int = 3
) -> NDArray[np.float64]:
    """Einfache gleitende Mittelwert-Glättung.

    Args:
        data: Array mit Messwerten.
        window: Fensterbreite (ungerade empfohlen).

    Returns:
        Geglättetes Array (gleiche Länge).
    """
    if window <= 1:
        return data.copy()
    pad = window // 2
    padded = np.pad(data, pad_width=pad, mode="edge")
    kernel = np.ones(window) / float(window)
    smoothed = np.convolve(padded, kernel, mode="valid")
    return smoothed


def derivatives(
    time_min: NDArray[np.float64], glucose: NDArray[np.float64]
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Berechne erste und zweite numerische Ableitung (zentrale Differenzen).

    Args:
        time_min: Zeitvektor in Minuten.
        glucose: Glukosemesswerte zum jeweiligen Zeitpunkt.

    Returns:
        Tuple (first_derivative, second_derivative).
    """
    g1 = np.gradient(glucose, time_min)
    g2 = np.gradient(g1, time_min)
    return g1, g2
