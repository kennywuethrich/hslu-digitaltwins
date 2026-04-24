"""Gemeinsame Start-Hilfe für Skripte im Projektwurzelverzeichnis."""

from pathlib import Path
import sys


def add_src_to_path() -> None:
    """Fügt den src-Ordner zum Python-Pfad hinzu.

    Dadurch können Root-Skripte wie app.py und demo.py das
    Paket glucose_insulin ohne doppelte Pfadlogik importieren.
    """
    project_root = Path(__file__).resolve().parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
