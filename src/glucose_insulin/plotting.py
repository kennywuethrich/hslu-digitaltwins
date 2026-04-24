"""Visualisierung für Simulationsergebnisse mit Matplotlib."""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from glucose_insulin.simulation import SimulationResult


def build_simulation_figure(result: SimulationResult) -> Figure:
    """Erzeugt eine Matplotlib-Figur für ein Simulationsergebnis.

    Args:
        result: Ergebnis einer Simulation.

    Returns:
        Matplotlib-Figur mit Glukose- und Insulinverlauf.
    """
    figure, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

    axes[0].plot(
        result.time_min,
        result.plasma_glucose,
        label="Plasma-Glukose",
        linewidth=2.0,
    )
    axes[0].plot(
        result.time_min,
        result.cgm_glucose,
        label="CGM-Glukose",
        linewidth=2.0,
        linestyle="--",
    )
    axes[0].set_ylabel("Glukose [mmol/L]")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(
        result.time_min,
        result.plasma_insulin,
        label="Plasma-Insulin",
        color="tab:orange",
        linewidth=2.0,
    )
    axes[1].set_xlabel("Zeit [min]")
    axes[1].set_ylabel("Insulin [pmol/L]")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    figure.suptitle("Glukose-Insulin-Simulation (T1D-Basismodell)")
    figure.tight_layout()
    return figure


def plot_simulation(result: SimulationResult) -> None:
    """Zeigt Glukose- und Insulinverlauf einer Simulation.

    Args:
        result: Ergebnis einer Simulation.
    """
    figure = build_simulation_figure(result)
    plt.show()
    plt.close(figure)
