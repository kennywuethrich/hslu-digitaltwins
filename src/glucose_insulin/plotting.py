"""Visualisierung für die Digital-Shadow-Ausgabe mit Matplotlib."""

from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import seaborn as sns
from numpy.typing import NDArray


def _figure_size_from_time(
    time_min: NDArray[np.float64],
) -> tuple[float, float]:
    """Leitet eine sinnvolle Figurgröße aus der Zeitreihe ab."""
    length = int(time_min.size)
    width = max(10.0, min(18.0, 8.0 + length / 80.0))
    height = 8.0
    return width, height


def build_policy_figure(
    time_min: NDArray[np.float64],
    glucose_mmol_l: NDArray[np.float64],
    insulin_rate: NDArray[np.float64],
) -> Figure:
    """Erzeugt die Standardfigur für den Digital-Shadow-Use-Case.

    Args:
        time_min: Zeitvektor [min].
        glucose_mmol_l: Gemessene CGM-Zeitreihe [mmol/L].
        insulin_rate: Berechnete Insulin-Zeitreihe [pmol/L/min].

    Returns:
        Matplotlib-Figur mit Messung und Insulinentscheidung.
    """
    if time_min.shape != glucose_mmol_l.shape:
        raise ValueError("time_min and glucose_mmol_l must have same shape")
    if time_min.shape != insulin_rate.shape:
        raise ValueError("time_min and insulin_rate must have same shape")

    figure_size = _figure_size_from_time(time_min)
    figure, axes = plt.subplots(2, 1, figsize=figure_size, sharex=True)

    axes[0].plot(
        time_min,
        glucose_mmol_l,
        label="Gemessene CGM-Glukose",
        color="tab:blue",
        linewidth=2.0,
    )
    axes[0].set_ylabel("Glukose [mmol/L]")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].step(
        time_min,
        insulin_rate,
        where="post",
        label="Insulinentscheidung",
        color="tab:orange",
        linewidth=2.0,
    )
    axes[1].set_xlabel("Zeit [min]")
    axes[1].set_ylabel("Insulin [pmol/L/min]")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    figure.suptitle("Digital Shadow: Messung und Insulinentscheidung")
    figure.tight_layout()
    return figure


def _minute_of_day(timestamp: datetime) -> float:
    """Berechnet die Minuten seit Mitternacht."""
    return float(
        timestamp.hour * 60 + timestamp.minute + timestamp.second / 60.0
    )


def build_daily_glucose_overlay_figure(
    timestamps: list[datetime],
    glucose_mmol_l: NDArray[np.float64],
) -> Figure:
    """Erzeugt einen Tages-Overlay-Plot für Glukose.

    Args:
        timestamps: Originale Zeitstempel der Messung.
        glucose_mmol_l: Gemessene Glukose [mmol/L].

    Returns:
        Matplotlib-Figur mit dünnen Tageslinien und Mittelwertlinie.
    """
    if len(timestamps) != glucose_mmol_l.shape[0]:
        raise ValueError("timestamps and glucose_mmol_l must have same length")

    frame = pd.DataFrame(
        {
            "timestamp": timestamps,
            "glucose_mmol_l": glucose_mmol_l,
        }
    )
    frame["day"] = frame["timestamp"].dt.date
    frame["minute_of_day"] = frame["timestamp"].map(_minute_of_day)

    figure, axis = plt.subplots(figsize=(12.0, 5.5))

    segments: list[np.ndarray] = []
    for _, day_frame in frame.groupby("day", sort=True):
        points = np.column_stack(
            [
                day_frame["minute_of_day"].to_numpy(),
                day_frame["glucose_mmol_l"].to_numpy(),
            ]
        )
        if points.shape[0] >= 2:
            segments.append(points)

    if segments:
        collection = LineCollection(
            segments,
            colors="0.75",
            linewidths=0.8,
            alpha=0.35,
            zorder=1,
        )
        axis.add_collection(collection)

    sns.lineplot(
        data=frame,
        x="minute_of_day",
        y="glucose_mmol_l",
        estimator="mean",
        errorbar=None,
        color="tab:blue",
        linewidth=2.8,
        ax=axis,
        zorder=3,
        legend=False,
    )

    axis.set_xlim(0.0, 24.0 * 60.0)
    axis.set_xlabel("Zeit im Tag [min]")
    axis.set_ylabel("Glukose [mmol/L]")
    axis.set_title("Tagesprofil der Glukose: dünne Tage, dicke Mittelkurve")
    axis.grid(True, alpha=0.25)
    axis.set_xticks([0, 360, 720, 1080, 1440])
    axis.set_xticklabels(["00:00", "06:00", "12:00", "18:00", "24:00"])
    figure.tight_layout()
    return figure
