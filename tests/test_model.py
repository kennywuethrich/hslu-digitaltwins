"""Unit tests for the direct CGM-to-insulin model."""

import numpy as np
import pytest

from glucose_insulin.model import GlucoseInsulinModel
from glucose_insulin.profiles import (
    meal_glucose_rate,
    rectangular_pulse,
)
from glucose_insulin.units import (
    mg_per_dl_to_mmol_per_l,
    mmol_per_l_to_mg_per_dl,
)


class TestGlucoseInsulinModel:
    """Tests for GlucoseInsulinModel."""

    def test_profile_length_matches_input(self) -> None:
        """The insulin profile must have the same length as the CGM data."""
        time_min = np.array([0.0, 5.0, 10.0], dtype=np.float64)
        glucose = np.array([5.0, 6.0, 8.0], dtype=np.float64)
        model = GlucoseInsulinModel()

        insulin_rate = model.build_profile(time_min, glucose)

        assert insulin_rate.shape == time_min.shape

    def test_insulin_increases_with_rising_glucose(self) -> None:
        """Rising glucose should produce a stronger insulin response."""
        time_min = np.array([0.0, 5.0, 10.0], dtype=np.float64)
        glucose = np.array([5.0, 6.5, 9.0], dtype=np.float64)
        model = GlucoseInsulinModel(target_mmol_l=6.0, kp=0.5)

        insulin_rate = model.build_profile(time_min, glucose)

        assert insulin_rate[-1] >= insulin_rate[0]

    def test_assistive_mode_uses_patient_profile(self) -> None:
        """Patient profile should override automatic dosing when present."""

        def patient_profile(_time_min: float) -> float:
            return 2.0

        time_min = np.array([0.0, 5.0, 10.0], dtype=np.float64)
        glucose = np.array([5.0, 5.5, 6.0], dtype=np.float64)
        model = GlucoseInsulinModel(patient_profile=patient_profile)

        insulin_rate = model.build_profile(time_min, glucose)

        assert insulin_rate[0] == pytest.approx(2.0)


class TestProfilesAndUnits:
    """Tests for profile and unit helper functions."""

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
