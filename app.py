"""Streamlit-App für den Digital-Shadow-Use-Case.

Start:
    streamlit run app.py
"""

from pathlib import Path

import numpy as np
import streamlit as st

from bootstrap import add_src_to_path

add_src_to_path()

from glucose_insulin.model import GlucoseInsulinModel
from glucose_insulin.plotting import (
    build_daily_glucose_overlay_figure,
    build_policy_figure,
)
from glucose_insulin.preprocessing import (
    derivatives,
    load_cgm_series,
    moving_average,
)

DATA_PATH = Path(__file__).resolve().parent / "data" / "CGM_Werte.csv"


def _run_use_case_1(time_min: np.ndarray, glucose_mmol_l: np.ndarray):
    """Berechnet den autonomen Insulinverlauf für UseCase 1."""
    model = GlucoseInsulinModel(
        target_mmol_l=float(np.median(glucose_mmol_l)),
        kp=0.25,
        max_rate=5.0,
        prediction_horizon_min=15.0,
    )
    return model.build_profile(time_min, glucose_mmol_l)


def _run_use_case_2(time_min: np.ndarray, glucose_mmol_l: np.ndarray):
    """Berechnet den assistiven Insulinverlauf für UseCase 2."""

    def patient_profile(current_time_min: float) -> float:
        if current_time_min < float(time_min[-1]) * 0.35:
            return 1.5
        return 0.0

    model = GlucoseInsulinModel(
        patient_profile=patient_profile,
        alert_threshold=float(np.percentile(glucose_mmol_l, 80)),
        kp=0.18,
        max_rate=5.0,
        prediction_horizon_min=15.0,
    )
    return model.build_profile(time_min, glucose_mmol_l)


def main() -> None:
    """Rendert die datengetriebene Oberfläche."""
    st.set_page_config(page_title="Digital Shadow", layout="wide")
    st.title("Glukose-Insulin Digital Shadow")
    st.caption(
        "Die App verwendet die reale CGM-Zeitreihe und zeigt zwei UseCases: "
        "autonome Insulinabgabe und assistive Eingriffe bei Vergessen."
    )

    series = load_cgm_series(DATA_PATH)
    smoothed_glucose = moving_average(series.glucose_mmol_l, window=5)
    first_derivative, second_derivative = derivatives(
        series.time_min,
        smoothed_glucose,
    )

    st.info(
        "Der Plot passt sich automatisch an die geladene Zeitreihe an. "
        "Es gibt keine festen Slider für Simulationsdauer oder Modellparameter."
    )

    use_case = st.radio(
        "UseCase",
        ["UseCase 1: autonom", "UseCase 2: assistiv"],
        horizontal=True,
    )

    if use_case == "UseCase 1: autonom":
        insulin_rate = _run_use_case_1(series.time_min, smoothed_glucose)
        st.subheader("UseCase 1: Autonome Insulinregelung")
        st.write(
            "Das System dosiert selbstständig anhand des aktuellen Verlaufs "
            "und einer kurzen Vorhersage über 15 Minuten."
        )
    else:
        insulin_rate = _run_use_case_2(series.time_min, smoothed_glucose)
        st.subheader("UseCase 2: Assistive Insulinregelung")
        st.write(
            "Der Patient gibt zunächst selbst Insulin ab, danach greift das "
            "System bei Vergessen oder hohem Glukosetrend ein."
        )

    figure = build_policy_figure(
        series.time_min,
        series.glucose_mmol_l,
        insulin_rate,
    )
    st.pyplot(figure, clear_figure=True)

    daily_figure = build_daily_glucose_overlay_figure(
        series.timestamps,
        series.glucose_mmol_l,
    )
    st.pyplot(daily_figure, clear_figure=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Messung Start [mmol/L]", f"{series.glucose_mmol_l[0]:.2f}")
    col2.metric("Messung Ende [mmol/L]", f"{series.glucose_mmol_l[-1]:.2f}")
    col3.metric("Steigung Ende", f"{float(first_derivative[-1]):.3f}")
    col4.metric("Krümmung Ende", f"{float(second_derivative[-1]):.3f}")

    st.caption(
        "Hinweis: Die Simulation ist ein vereinfachter Digital Shadow und "
        "kein validierter medizinischer Zwilling."
    )


if __name__ == "__main__":
    main()
