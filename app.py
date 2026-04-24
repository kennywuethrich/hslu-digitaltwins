"""Interaktive Streamlit-App für das T1D-Basismodell.

Start:
    streamlit run app.py
"""

import streamlit as st

from bootstrap import add_src_to_path

add_src_to_path()

from config.metrics import glucose_metrics
from config.scenarios import (
    build_runtime,
    list_preset_names,
    preset_values,
)
from config.ui_config import SLIDER_SPECS
from glucose_insulin.model import GlucoseInsulinModel
from glucose_insulin.plotting import build_simulation_figure
from glucose_insulin.simulation import run_simulation


def slider_value(values: dict[str, float], key: str) -> float:
    """Liest einen Sliderwert anhand der zentralen UI-Konfiguration."""
    spec = SLIDER_SPECS[key]
    kwargs: dict[str, object] = {
        "label": spec.label,
        "min_value": spec.min_value,
        "max_value": spec.max_value,
        "value": float(values[key]),
        "step": spec.step,
    }
    if spec.number_format is not None:
        kwargs["format"] = spec.number_format
    return float(st.sidebar.slider(**kwargs))


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
        list_preset_names(),
    )
    values = preset_values(preset_name)

    st.sidebar.subheader("Use-Case")
    values["meal_glucose_mmol"] = slider_value(values, "meal_glucose_mmol")
    values["absorption_rate_min"] = slider_value(
        values,
        "absorption_rate_min",
    )
    values["duration_min"] = slider_value(values, "duration_min")

    st.sidebar.subheader("Aktivität")
    values["activity_start_min"] = slider_value(values, "activity_start_min")
    values["activity_end_min"] = slider_value(values, "activity_end_min")
    values["activity_height"] = slider_value(values, "activity_height")

    st.sidebar.subheader("Exogenes Insulin")
    values["insulin_start_min"] = slider_value(values, "insulin_start_min")
    values["insulin_end_min"] = slider_value(values, "insulin_end_min")
    values["insulin_height"] = slider_value(values, "insulin_height")

    st.sidebar.subheader("Modellparameter")
    values["k1"] = slider_value(values, "k1")
    values["k2"] = slider_value(values, "k2")
    values["k3"] = slider_value(values, "k3")
    values["k4"] = slider_value(values, "k4")
    values["endogenous_insulin_height"] = slider_value(
        values,
        "endogenous_insulin_height",
    )

    invalid_activity_window = (
        values["activity_end_min"] <= values["activity_start_min"]
    )
    invalid_insulin_window = (
        values["insulin_end_min"] <= values["insulin_start_min"]
    )
    if invalid_activity_window or invalid_insulin_window:
        st.error("Bitte Start/Ende so wählen, dass Ende > Start ist.")
        return

    runtime = build_runtime(values, n_points=600)
    model = GlucoseInsulinModel(parameters=runtime.model_parameters)
    result = run_simulation(
        model=model,
        config=runtime.simulation_config,
        profiles=runtime.input_profiles,
    )
    summary = glucose_metrics(result)

    figure = build_simulation_figure(result)
    st.pyplot(figure, clear_figure=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Max Glukose [mmol/L]", f"{summary.max_glucose_mmol_l:.2f}")
    c2.metric("Min Glukose [mmol/L]", f"{summary.min_glucose_mmol_l:.2f}")
    c3.metric("Endwert Glukose [mmol/L]", f"{summary.end_glucose_mmol_l:.2f}")


if __name__ == "__main__":
    main()
