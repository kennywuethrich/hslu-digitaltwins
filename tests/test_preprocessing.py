"""Tests for CGM preprocessing helpers."""

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

from glucose_insulin.plotting import build_daily_glucose_overlay_figure
from glucose_insulin.preprocessing import (
    derivatives,
    load_cgm_series,
    moving_average,
)


class TestPreprocessing:
    """Tests for preprocessing helpers."""

    def test_load_cgm_series_reads_glucose_values(self) -> None:
        """The loader should return the measured glucose values."""
        csv_path = (
            Path(__file__).resolve().parents[1] / "data" / "CGM_Werte.csv"
        )
        series = load_cgm_series(csv_path)
        assert series.time_min.shape == series.glucose_mmol_l.shape
        assert series.time_min.size > 0
        assert len(series.timestamps) == series.time_min.size
        assert float(series.glucose_mmol_l[0]) == 4.7

    def test_load_cgm_series_reads_alternate_schema(self) -> None:
        """The loader should also accept bg_ts/value CSV files."""
        csv_path = (
            Path(__file__).resolve().parents[1] / "data" / "CGM_data_diab1.csv"
        )
        series = load_cgm_series(csv_path)
        assert series.time_min.shape == series.glucose_mmol_l.shape
        assert series.time_min.size > 0
        assert len(series.timestamps) == series.time_min.size
        assert float(series.glucose_mmol_l[0]) == 7.5

    def test_daily_glucose_overlay_returns_figure(self) -> None:
        """The daily overlay helper should return a Matplotlib figure."""
        csv_path = (
            Path(__file__).resolve().parents[1] / "data" / "CGM_Werte.csv"
        )
        series = load_cgm_series(csv_path)
        figure = build_daily_glucose_overlay_figure(
            series.timestamps,
            series.glucose_mmol_l,
        )
        assert isinstance(figure, Figure)

    def test_moving_average_preserves_length(self) -> None:
        """Smoothing should keep the same array length."""
        data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)
        smoothed = moving_average(data, window=3)
        assert smoothed.shape == data.shape

    def test_derivatives_return_two_arrays(self) -> None:
        """Derivative helper should return first and second derivative."""
        time_min = np.array([0.0, 5.0, 10.0], dtype=np.float64)
        glucose = np.array([4.0, 5.0, 7.0], dtype=np.float64)
        g1, g2 = derivatives(time_min, glucose)
        assert g1.shape == glucose.shape
        assert g2.shape == glucose.shape
