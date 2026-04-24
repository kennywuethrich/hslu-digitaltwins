"""Unit tests for the glucose-insulin compartment model.

Tests verify structural correctness and basic numerical properties of
the model and utility functions. Full physiological validation will be
added in SW10 once model equations are finalised.
"""

import pytest

from config.metrics import glucose_metrics
from config.scenarios import build_runtime, preset_values
from glucose_insulin.model import (
    GlucoseInsulinModel,
    ModelInputs,
    ModelParameters,
)
from glucose_insulin.simulation import (
    InputProfiles,
    SimulationConfig,
    run_simulation,
)
from glucose_insulin.utils import (
    meal_glucose_rate,
    mg_per_dl_to_mmol_per_l,
    mmol_per_l_to_mg_per_dl,
    rectangular_pulse,
)


class TestModelParameters:
    """Tests for ModelParameters dataclass."""

    def test_default_basal_glucose_is_physiological(self) -> None:
        """Basal glucose should be in normal fasting range (4–6 mmol/L)."""
        params = ModelParameters()
        assert 4.0 <= params.glucose_basal <= 6.0

    def test_default_basal_insulin_is_positive(self) -> None:
        """Basal insulin must be strictly positive."""
        params = ModelParameters()
        assert params.insulin_basal > 0.0


class TestGlucoseInsulinModel:
    """Tests for GlucoseInsulinModel."""

    def test_initial_state_shape(self) -> None:
        """Initial state vector must have exactly 3 elements."""
        model = GlucoseInsulinModel()
        x0 = model.initial_state()
        assert x0.shape == (3,)

    def test_initial_state_matches_basal(self) -> None:
        """Plasma glucose and interstitial glucose start at basal."""
        model = GlucoseInsulinModel()
        x0 = model.initial_state()
        assert x0[0] == pytest.approx(model.parameters.glucose_basal)
        assert x0[2] == pytest.approx(model.parameters.glucose_basal)

    def test_odes_return_shape(self) -> None:
        """ODE right-hand side must return vector of same shape as state."""
        model = GlucoseInsulinModel()
        x0 = model.initial_state()
        dxdt = model.odes(0.0, x0, inputs=ModelInputs())
        assert dxdt.shape == x0.shape

    def test_activity_reduces_glucose_derivative(self) -> None:
        """Activity input must reduce glucose derivative in dG/dt."""
        model = GlucoseInsulinModel()
        x0 = model.initial_state()
        with_activity = model.odes(
            0.0,
            x0,
            inputs=ModelInputs(meal_rate=1.0, activity_rate=0.4),
        )
        without_activity = model.odes(
            0.0,
            x0,
            inputs=ModelInputs(meal_rate=1.0, activity_rate=0.0),
        )
        assert with_activity[0] < without_activity[0]

    def test_cgm_output_returns_interstitial(self) -> None:
        """CGM output must equal the interstitial glucose state."""
        model = GlucoseInsulinModel()
        x0 = model.initial_state()
        assert model.cgm_output(x0) == pytest.approx(x0[2])


class TestSimulation:
    """Tests for the simulation runner."""

    def test_run_simulation_output_length(self) -> None:
        """Result arrays must have the requested number of points."""
        model = GlucoseInsulinModel()
        result = run_simulation(
            model,
            config=SimulationConfig(meal_glucose_mmol=50.0, n_points=100),
        )
        assert len(result.time_min) == 100
        assert len(result.cgm_glucose) == 100

    def test_run_simulation_time_starts_at_zero(self) -> None:
        """Simulation time must start at t=0."""
        model = GlucoseInsulinModel()
        result = run_simulation(
            model,
            config=SimulationConfig(meal_glucose_mmol=50.0),
        )
        assert result.time_min[0] == pytest.approx(0.0)

    def test_run_simulation_with_activity_profile(self) -> None:
        """Simulation must accept external activity profile callback."""
        model = GlucoseInsulinModel()

        def activity_rate(_time_min: float) -> float:
            return 0.05

        result = run_simulation(
            model,
            config=SimulationConfig(meal_glucose_mmol=50.0),
            profiles=InputProfiles(activity_rate_fn=activity_rate),
        )
        assert len(result.time_min) == 500


class TestUtils:
    """Tests for utility functions."""

    def test_meal_glucose_rate_at_zero(self) -> None:
        """Rate at t=0 should equal total_dose / tau."""
        rate = meal_glucose_rate(
            time_min=0.0,
            total_glucose_mmol=30.0,
            absorption_rate_min=30.0,
        )
        assert rate == pytest.approx(1.0)  # 30/30 * exp(0) = 1.0

    def test_meal_glucose_rate_decays(self) -> None:
        """Rate must decrease monotonically over time."""
        rates = [
            meal_glucose_rate(t, total_glucose_mmol=50.0)
            for t in [0, 10, 30, 60, 120]
        ]
        assert all(rates[i] > rates[i + 1] for i in range(len(rates) - 1))

    def test_meal_glucose_rate_negative_dose_raises(self) -> None:
        """Negative meal dose must raise ValueError."""
        with pytest.raises(ValueError):
            meal_glucose_rate(0.0, total_glucose_mmol=-10.0)

    def test_meal_glucose_rate_zero_dose_is_zero(self) -> None:
        """Zero meal dose must yield zero glucose rate."""
        assert meal_glucose_rate(0.0, total_glucose_mmol=0.0) == 0.0

    def test_unit_conversion_roundtrip(self) -> None:
        """mmol/L → mg/dL → mmol/L must be a lossless roundtrip."""
        original = 5.5
        converted = mmol_per_l_to_mg_per_dl(original)
        restored = mg_per_dl_to_mmol_per_l(converted)
        assert restored == pytest.approx(original, rel=1e-9)

    def test_rectangular_pulse_inside_interval(self) -> None:
        """Pulse must return height inside the configured interval."""
        value = rectangular_pulse(
            10.0, start_min=5.0, end_min=15.0, height=2.0
        )
        assert value == pytest.approx(2.0)


class TestScenarioRuntime:
    """Tests für die zentrale Szenario->Runtime-Abbildung."""

    def test_build_runtime_uses_given_n_points(self) -> None:
        """Runtime builder must propagate n_points to simulation config."""
        values = preset_values("Mahlzeit mit Bewegung")
        runtime = build_runtime(values, n_points=123)
        assert runtime.simulation_config.n_points == 123


class TestMetrics:
    """Tests für zentrale Ergebnis-Metriken."""

    def test_glucose_metrics_returns_consistent_values(self) -> None:
        """Metric helper must return consistent max/min/end values."""
        model = GlucoseInsulinModel()
        result = run_simulation(
            model,
            config=SimulationConfig(meal_glucose_mmol=50.0, n_points=50),
        )
        summary = glucose_metrics(result)
        assert summary.max_glucose_mmol_l >= summary.min_glucose_mmol_l
        assert summary.end_glucose_mmol_l == pytest.approx(
            float(result.plasma_glucose[-1])
        )
