"""Zentrale UI-Konfiguration fuer Streamlit-Slider."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SliderSpec:
    """Beschreibt einen Streamlit-Slider.

    Attributes:
        label: Sichtbarer Text in der UI.
        min_value: Minimalwert.
        max_value: Maximalwert.
        step: Schrittweite.
        number_format: Optionales Anzeigeformat.
    """

    label: str
    min_value: float
    max_value: float
    step: float
    number_format: str | None = None


SLIDER_SPECS: dict[str, SliderSpec] = {
    "meal_glucose_mmol": SliderSpec("Mahlzeit [mmol]", 0.0, 120.0, 1.0),
    "absorption_rate_min": SliderSpec(
        "Absorptionszeit [min]",
        10.0,
        90.0,
        1.0,
    ),
    "duration_min": SliderSpec("Simulationsdauer [min]", 60.0, 480.0, 10.0),
    "activity_start_min": SliderSpec("Aktivität Start [min]", 0.0, 400.0, 1.0),
    "activity_end_min": SliderSpec("Aktivität Ende [min]", 1.0, 480.0, 1.0),
    "activity_height": SliderSpec("Aktivität Intensität", 0.0, 0.4, 0.01),
    "insulin_start_min": SliderSpec("Insulin Start [min]", 0.0, 400.0, 1.0),
    "insulin_end_min": SliderSpec("Insulin Ende [min]", 1.0, 480.0, 1.0),
    "insulin_height": SliderSpec("Insulinrate exogen", 0.0, 0.3, 0.01),
    "k1": SliderSpec("k1", 0.0, 0.05, 0.001),
    "k2": SliderSpec("k2", 0.0, 0.005, 0.0001, "%.4f"),
    "k3": SliderSpec("k3", 0.0, 1.0, 0.01),
    "k4": SliderSpec("k4", 0.0, 0.2, 0.005),
    "endogenous_insulin_height": SliderSpec(
        "Endogenes Insulin (konstant)",
        0.0,
        0.2,
        0.01,
    ),
}
