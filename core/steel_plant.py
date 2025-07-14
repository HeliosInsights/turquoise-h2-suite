"""Simplified steel plant model hooking in hydrogen supply blocks."""
from typing import Dict, Sequence

from supply import HazerSupply, ElectrolysisSupply
from energy import RenewableSupply


SUPPLY_MAP = {
    'hazer': HazerSupply,
    'electrolysis': ElectrolysisSupply,
    'renewable': RenewableSupply,
}


def run_steel_plant(
    demand_profile: Sequence[float],
    supply_type: str = 'hazer',
    solar: Sequence[float] | None = None,
    wind: Sequence[float] | None = None,
) -> Dict[str, float]:
    """Compute rough cost and emission results for a steel plant."""
    SupplyCls = SUPPLY_MAP[supply_type]
    if supply_type == 'renewable':
        if solar is None or wind is None:
            raise ValueError('solar and wind traces required for renewable supply')
        supply = SupplyCls(demand_profile, solar, wind)
    else:
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
