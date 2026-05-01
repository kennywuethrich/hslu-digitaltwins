"""Einfache Demo für den Digital-Shadow-Use-Case.

Start:
    python demo.py
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from bootstrap import add_src_to_path

add_src_to_path()

from glucose_insulin.model import GlucoseInsulinModel
from glucose_insulin.plotting import (
    build_daily_glucose_overlay_figure,
    build_policy_figure,
)
from glucose_insulin.preprocessing import load_cgm_series

DATA_PATH = Path(__file__).resolve().parent / "data" / "CGM_Werte.csv"


def _run_autonomous(series_time_min: np.ndarray, series_glucose: np.ndarray):
    """Berechnet UseCase 1 mit autonomer Insulingabe."""
    model = GlucoseInsulinModel(target_mmol_l=6.0, kp=0.25)
    return model.build_profile(series_time_min, series_glucose)


def _run_assistive(series_time_min: np.ndarray, series_glucose: np.ndarray):
    """Berechnet UseCase 2 mit assistiver Eingabe."""

    def patient_profile(current_time_min: float) -> float:
        if current_time_min < float(series_time_min[-1]) * 0.35:
            return 1.5
        return 0.0

    model = GlucoseInsulinModel(
        patient_profile=patient_profile,
        alert_threshold=8.0,
        kp=0.18,
    )
    return model.build_profile(series_time_min, series_glucose)


def main() -> None:
    """Startet beide UseCases mit der echten CGM-Zeitreihe."""
    series = load_cgm_series(DATA_PATH)

    insulin_one = _run_autonomous(series.time_min, series.glucose_mmol_l)
    figure_one = build_policy_figure(
        series.time_min,
        series.glucose_mmol_l,
        insulin_one,
    )
    figure_one.suptitle("UseCase 1: autonome Insulingabe")
    plt.show()
    plt.close(figure_one)

    daily_figure = build_daily_glucose_overlay_figure(
        series.timestamps,
        series.glucose_mmol_l,
    )
    daily_figure.suptitle("Tagesprofil: Glukose")
    plt.show()
    plt.close(daily_figure)

    insulin_two = _run_assistive(series.time_min, series.glucose_mmol_l)
    figure_two = build_policy_figure(
        series.time_min,
        series.glucose_mmol_l,
        insulin_two,
    )
    figure_two.suptitle("UseCase 2: assistive Insulingabe")
    plt.show()
    plt.close(figure_two)


if __name__ == "__main__":
    main()
