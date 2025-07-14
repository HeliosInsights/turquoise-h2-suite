from dataclasses import dataclass
from typing import Dict, Any, Sequence
from statistics import mean

from .base import SupplyBlock


elec_price_default = 50 / 1e3  # USD per kWh => per MWh /1000


@dataclass
class ElectrolysisParams:
    efficiency: float = 50  # kWh/kg H2
    capex_per_kw: float = 700  # USD per kW
    fixed_opex_frac: float = 0.04


class ElectrolysisSupply(SupplyBlock):
    """Simplified electrolytic hydrogen supply."""

    def __init__(self, demand_profile: Sequence[float], params: ElectrolysisParams | None = None, elec_price: float = elec_price_default):
        super().__init__(demand_profile)
        self.params = params or ElectrolysisParams()
        self.elec_price = elec_price

    def mass_energy(self) -> Dict[str, float]:
        h2 = list(self.demand)
        electricity = [x * self.params.efficiency / 1000 for x in h2]  # kWh/kg -> MWh/t
        return {
            "H2": float(sum(h2)),
            "Electricity": float(sum(electricity)),
        }

    def capex_opex(self) -> Dict[str, Any]:
        rate = mean(self.demand)
        power_kw = rate * self.params.efficiency
        capex = power_kw * self.params.capex_per_kw
        fuel_cost = self.mass_energy()["Electricity"] * 1000 * self.elec_price
        annualised = 0.1 * capex
        lcoh = (annualised + fuel_cost) / self.mass_energy()["H2"]
        return {
            "capex": capex,
            "power_cost": fuel_cost,
            "lcoh": lcoh,
        }

    def lca(self) -> Dict[str, float]:
        flows = self.mass_energy()
        # Electricity use is in MWh; apply 18 kg CO2/MWh (18 g/kWh).
        co2_grid = flows["Electricity"] * 18
        return {
            "kg_co2_per_kg_h2": co2_grid / flows["H2"],
            "total_kg_co2": co2_grid,
        }
