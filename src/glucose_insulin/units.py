"""Einheitenumrechnungen für Glukosewerte."""


def mmol_per_l_to_mg_per_dl(value_mmol_l: float) -> float:
    """Konvertiert Blutglukose von mmol/L nach mg/dL.

    Args:
        value_mmol_l: Glucose concentration [mmol/L].

    Returns:
        Glucose concentration [mg/dL].
    """
    return value_mmol_l * 18.0182


def mg_per_dl_to_mmol_per_l(value_mg_dl: float) -> float:
    """Konvertiert Blutglukose von mg/dL nach mmol/L.

    Args:
        value_mg_dl: Glucose concentration [mg/dL].

    Returns:
        Glucose concentration [mmol/L].
    """
    return value_mg_dl / 18.0182


__all__ = ["mg_per_dl_to_mmol_per_l", "mmol_per_l_to_mg_per_dl"]