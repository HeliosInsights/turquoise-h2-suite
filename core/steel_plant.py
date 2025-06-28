"""Simplified steel plant model hooking in hydrogen supply blocks."""
from typing import Dict, Sequence

from supply import HazerSupply, ElectrolysisSupply


SUPPLY_MAP = {
    'hazer': HazerSupply,
    'electrolysis': ElectrolysisSupply,
}


def run_steel_plant(demand_profile: Sequence[float], supply_type: str = 'hazer') -> Dict[str, float]:
    """Compute rough cost and emission results for a steel plant."""
    SupplyCls = SUPPLY_MAP[supply_type]
    supply = SupplyCls(demand_profile)

    flows = supply.mass_energy()
    costs = supply.capex_opex()
    impacts = supply.lca()

    return {
        'h2_kg': flows['H2'],
        'supply_capex': costs['capex'],
        'lcoh': costs['lcoh'],
        'supply_emissions_kg': impacts['total_kg_co2'],
    }
