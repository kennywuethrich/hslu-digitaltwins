"""Zentrale Szenario-Definitionen fuer Demo und Streamlit-App."""

from dataclasses import dataclass
from typing import Callable

from glucose_insulin.model import ModelParameters
from glucose_insulin.simulation import InputProfiles, SimulationConfig
from glucose_insulin.utils import rectangular_pulse

ScenarioValues = dict[str, float]
ScenarioProfiles = Callable[[float], float]

DEFAULT_SCENARIO = "Mahlzeit mit Bewegung"


@dataclass
class ScenarioRuntime:
    """Fertig aufbereitete Objekte fuer eine Simulation.

    Attributes:
        model_parameters: Modellparameter fuer Glukose-Insulin-Dynamik.
        simulation_config: Laufzeit- und Mahlzeitkonfiguration.
        input_profiles: Externe Eingangsprofile fuer Aktivität/Insulin.
    """

    model_parameters: ModelParameters
    simulation_config: SimulationConfig
    input_profiles: InputProfiles


_PRESETS: dict[str, ScenarioValues] = {
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


def list_preset_names() -> list[str]:
    """Gibt alle verfuegbaren Preset-Namen zurueck."""
    return list(_PRESETS.keys())


def preset_values(preset_name: str) -> ScenarioValues:
    """Liefert die Werte eines Szenario-Presets.

    Args:
        preset_name: Name des gewuenschten Presets.

    Returns:
        Kopie der Preset-Werte.

    Raises:
        ValueError: Falls der Preset-Name unbekannt ist.
    """
    if preset_name not in _PRESETS:
        raise ValueError(f"Unknown preset_name: {preset_name}")
    return dict(_PRESETS[preset_name])


def pulse_profile(
    start_min: float,
    end_min: float,
    height: float,
) -> ScenarioProfiles:
    """Erzeugt ein rechteckiges Eingangsprofil mit fixer Hoehe."""

    def profile(time_min: float) -> float:
        return rectangular_pulse(
            time_min=time_min,
            start_min=start_min,
            end_min=end_min,
            height=height,
        )

    return profile


def build_runtime(values: ScenarioValues, n_points: int) -> ScenarioRuntime:
    """Erzeugt Runtime-Objekte aus Szenariowerten.

    Args:
        values: Szenariowerte aus einem Preset oder UI.
        n_points: Anzahl Simulationspunkte.

    Returns:
        ScenarioRuntime mit Parametern, Konfiguration und Profilen.
    """
    model_parameters = ModelParameters(
        glucose_basal=5.0,
        insulin_basal=10.0,
        k1=values["k1"],
        k2=values["k2"],
        k3=values["k3"],
        k4=values["k4"],
    )
    simulation_config = SimulationConfig(
        meal_glucose_mmol=values["meal_glucose_mmol"],
        duration_min=values["duration_min"],
        absorption_rate_min=values["absorption_rate_min"],
        n_points=n_points,
    )
    input_profiles = InputProfiles(
        activity_rate_fn=pulse_profile(
            start_min=values["activity_start_min"],
            end_min=values["activity_end_min"],
            height=values["activity_height"],
        ),
        endogenous_insulin_rate_fn=lambda _t: values[
            "endogenous_insulin_height"
        ],
        exogenous_insulin_rate_fn=pulse_profile(
            start_min=values["insulin_start_min"],
            end_min=values["insulin_end_min"],
            height=values["insulin_height"],
        ),
    )
    return ScenarioRuntime(
        model_parameters=model_parameters,
        simulation_config=simulation_config,
        input_profiles=input_profiles,
    )
