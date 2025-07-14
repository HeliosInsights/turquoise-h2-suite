"""Minimal enthalpy utilities ported from HDRI-EAF project."""
from __future__ import annotations

# Constant heat capacities at 25C (J/mol/K)
CP = {
    "CH4": 35.69,   # methane
    "H2": 28.84,    # hydrogen
    "C": 8.53,      # graphite
    "Fe": 25.1,     # iron approximate
}

MOLAR_MASS = {
    "CH4": 16.04,   # kg/kmol
    "H2": 2.016,
    "C": 12.01,
    "Fe": 55.85,
}


def mass_to_mol(species: str, mass_kg: float) -> float:
    """Convert kg to mol."""
    return mass_kg * 1e3 / MOLAR_MASS[species]


def sensible_enthalpy(species: str, t1_c: float, t2_c: float) -> float:
    """Return sensible enthalpy change in kJ/mol between two temperatures (C)."""
    cp = CP[species]
    return cp * (t2_c - t1_c) / 1000.0  # kJ/mol


def reaction_heat_per_mol_h2() -> float:
    """Standard enthalpy for CH4 -> C + 2 H2 per mol H2 (kJ)."""
    return 37.0


LHV = {
    "CH4": 50.0,   # MJ/kg
    "H2": 120.0,
}


def lhv(species: str) -> float:
    return LHV.get(species, 0.0)
