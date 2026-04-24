"""Interaktive Streamlit-App für das T1D-Basismodell.

Start:
    streamlit run app.py
"""

from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from glucose_insulin.model import GlucoseInsulinModel, ModelParameters
from glucose_insulin.plotting import build_simulation_figure
from glucose_insulin.simulation import (
    InputProfiles,
    SimulationConfig,
    run_simulation,
)
from glucose_insulin.utils import rectangular_pulse


def pulse_profile(
    start_min: float,
    end_min: float,
    height: float,
):
    """Erzeugt ein rechteckiges Zeitprofil mit fixer Höhe."""

    def profile(time_min: float) -> float:
        return rectangular_pulse(
            time_min=time_min,
            start_min=start_min,
            end_min=end_min,
            height=height,
        )

    return profile


def apply_preset(preset_name: str) -> dict[str, float]:
    """Liefert Standardwerte für ein Szenario."""
    presets: dict[str, dict[str, float]] = {
        "Ruhiger Alltag": {
            "meal_glucose_mmol": 60.0,
            "absorption_rate_min": 30.0,
            "duration_min": 240.0,
            "activity_start_min": 120.0,
            "activity_end_min": 150.0,
            "activity_height": 0.06,
            "insulin_start_min": 5.0,
            "insulin_end_min": 20.0,
            "insulin_height": 0.07,
            "k1": 0.01,
            "k2": 0.0005,
            "k3": 0.5,
            "k4": 0.05,
            "endogenous_insulin_height": 0.0,
        },
        "Mahlzeit ohne Bolus": {
            "meal_glucose_mmol": 75.0,
            "absorption_rate_min": 28.0,
            "duration_min": 240.0,
            "activity_start_min": 200.0,
            "activity_end_min": 220.0,
            "activity_height": 0.02,
            "insulin_start_min": 5.0,
            "insulin_end_min": 5.5,
            "insulin_height": 0.0,
            "k1": 0.01,
            "k2": 0.0005,
            "k3": 0.5,
            "k4": 0.05,
            "endogenous_insulin_height": 0.0,
        },
        "Mahlzeit mit Bewegung": {
            "meal_glucose_mmol": 65.0,
            "absorption_rate_min": 30.0,
            "duration_min": 240.0,
            "activity_start_min": 90.0,
            "activity_end_min": 130.0,
            "activity_height": 0.12,
            "insulin_start_min": 5.0,
            "insulin_end_min": 20.0,
            "insulin_height": 0.08,
            "k1": 0.01,
            "k2": 0.0005,
            "k3": 0.5,
            "k4": 0.05,
            "endogenous_insulin_height": 0.0,
        },
    }
    return presets[preset_name]


def main() -> None:
    """Rendert die interaktive Oberfläche."""
    st.set_page_config(page_title="T1D Digital Twin", layout="wide")
    st.title("Interaktive T1D-Simulation")
    st.caption(
        "Einfache, erklärbare Oberfläche auf Basis des bestehenden"
        " ODE-Modells."
    )

    preset_name = st.sidebar.selectbox(
        "Szenario-Preset",
        ["Ruhiger Alltag", "Mahlzeit ohne Bolus", "Mahlzeit mit Bewegung"],
    )
    values = apply_preset(preset_name)

    st.sidebar.subheader("Use-Case")
    meal_glucose_mmol = st.sidebar.slider(
        "Mahlzeit [mmol]",
        min_value=0.0,
        max_value=120.0,
        value=float(values["meal_glucose_mmol"]),
        step=1.0,
    )
    absorption_rate_min = st.sidebar.slider(
        "Absorptionszeit [min]",
        min_value=10.0,
        max_value=90.0,
        value=float(values["absorption_rate_min"]),
        step=1.0,
    )
    duration_min = st.sidebar.slider(
        "Simulationsdauer [min]",
        min_value=60.0,
        max_value=480.0,
        value=float(values["duration_min"]),
        step=10.0,
    )

    st.sidebar.subheader("Aktivität")
    activity_start_min = st.sidebar.slider(
        "Aktivität Start [min]",
        min_value=0.0,
        max_value=400.0,
        value=float(values["activity_start_min"]),
        step=1.0,
    )
    activity_end_min = st.sidebar.slider(
        "Aktivität Ende [min]",
        min_value=1.0,
        max_value=480.0,
        value=float(values["activity_end_min"]),
        step=1.0,
    )
    activity_height = st.sidebar.slider(
        "Aktivität Intensität",
        min_value=0.0,
        max_value=0.4,
        value=float(values["activity_height"]),
        step=0.01,
    )

    st.sidebar.subheader("Exogenes Insulin")
    insulin_start_min = st.sidebar.slider(
        "Insulin Start [min]",
        min_value=0.0,
        max_value=400.0,
        value=float(values["insulin_start_min"]),
        step=1.0,
    )
    insulin_end_min = st.sidebar.slider(
        "Insulin Ende [min]",
        min_value=1.0,
        max_value=480.0,
        value=float(values["insulin_end_min"]),
        step=1.0,
    )
    insulin_height = st.sidebar.slider(
        "Insulinrate exogen",
        min_value=0.0,
        max_value=0.3,
        value=float(values["insulin_height"]),
        step=0.01,
    )

    st.sidebar.subheader("Modellparameter")
    k1 = st.sidebar.slider(
        "k1",
        min_value=0.0,
        max_value=0.05,
        value=float(values["k1"]),
        step=0.001,
    )
    k2 = st.sidebar.slider(
        "k2",
        min_value=0.0,
        max_value=0.005,
        value=float(values["k2"]),
        step=0.0001,
        format="%.4f",
    )
    k3 = st.sidebar.slider(
        "k3",
        min_value=0.0,
        max_value=1.0,
        value=float(values["k3"]),
        step=0.01,
    )
    k4 = st.sidebar.slider(
        "k4",
        min_value=0.0,
        max_value=0.2,
        value=float(values["k4"]),
        step=0.005,
    )

    endogenous_insulin_height = st.sidebar.slider(
        "Endogenes Insulin (konstant)",
        min_value=0.0,
        max_value=0.2,
        value=float(values["endogenous_insulin_height"]),
        step=0.01,
    )

    invalid_activity_window = activity_end_min <= activity_start_min
    invalid_insulin_window = insulin_end_min <= insulin_start_min
    if invalid_activity_window or invalid_insulin_window:
        st.error("Bitte Start/Ende so wählen, dass Ende > Start ist.")
        return

    model = GlucoseInsulinModel(
        parameters=ModelParameters(
            glucose_basal=5.0,
            insulin_basal=10.0,
            k1=k1,
            k2=k2,
            k3=k3,
            k4=k4,
        )
    )

    config = SimulationConfig(
        meal_glucose_mmol=meal_glucose_mmol,
        duration_min=duration_min,
        absorption_rate_min=absorption_rate_min,
        n_points=600,
    )
    profiles = InputProfiles(
        activity_rate_fn=pulse_profile(
            start_min=activity_start_min,
            end_min=activity_end_min,
            height=activity_height,
        ),
        endogenous_insulin_rate_fn=lambda _t: endogenous_insulin_height,
        exogenous_insulin_rate_fn=pulse_profile(
            start_min=insulin_start_min,
            end_min=insulin_end_min,
            height=insulin_height,
        ),
    )

    result = run_simulation(model=model, config=config, profiles=profiles)

    figure = build_simulation_figure(result)
    st.pyplot(figure, clear_figure=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Max Glukose [mmol/L]", f"{result.plasma_glucose.max():.2f}")
    c2.metric("Min Glukose [mmol/L]", f"{result.plasma_glucose.min():.2f}")
    c3.metric("Endwert Glukose [mmol/L]", f"{result.plasma_glucose[-1]:.2f}")


if __name__ == "__main__":
    main()
