from dataclasses import dataclass
from typing import Dict, Any, Sequence
from statistics import mean

from .base import SupplyBlock


@dataclass
class HazerParams:
    """Key parameters for a Hazer-style methane pyrolysis plant."""
    ch4_per_h2: float = 3.8  # kg CH4 per kg H2
    elec_per_h2: float = 0.10  # MWh per t H2
    capex_per_tpd: float = 12e6  # USD per t H2/day of capacity
    graphite_per_h2: float = 2.9  # kg graphite per kg H2
    graphite_price: float = 0.5  # USD per kg
    ng_price: float = 3.5 / 1e6 * 3600  # USD per kg (3.5 $/GJ)
    leakage: float = 0.005  # fraction of CH4 that leaks


class HazerSupply(SupplyBlock):
    """Methane pyrolysis supply block using Hazer parameters."""

    def __init__(self, demand_profile: Sequence[float], params: HazerParams | None = None):
        super().__init__(demand_profile)
        self.params = params or HazerParams()

    def mass_energy(self) -> Dict[str, float]:
        h2 = list(self.demand)
        ch4 = [x * self.params.ch4_per_h2 for x in h2]
        elec = [x * self.params.elec_per_h2 / 1000 for x in h2]  # convert to GWh
        return {
            "H2": float(sum(h2)),
            "CH4": float(sum(ch4)),
            "Electricity": float(sum(elec)),
        }

    def capex_opex(self) -> Dict[str, Any]:
        avg_rate = mean(self.demand)  # kg/h
        size_tpd = avg_rate * 24 / 1000  # t H2/day
        capex = size_tpd * self.params.capex_per_tpd
        graphite_rev = sum(self.demand) * self.params.graphite_per_h2 * self.params.graphite_price
        fuel_cost = self.mass_energy()["CH4"] * self.params.ng_price
        annualised = 0.1 * capex  # 10 % capital recovery as placeholder
        lcoh = (annualised + fuel_cost - graphite_rev) / self.mass_energy()["H2"]
        return {
            "capex": capex,
            "fuel_cost": fuel_cost,
            "graphite_revenue": graphite_rev,
            "lcoh": lcoh,
        }

    def lca(self) -> Dict[str, float]:
        flows = self.mass_energy()
        co2_leakage = flows["CH4"] * self.params.leakage * 2.75  # kg CO2 from CH4 leak
        # Electricity is tracked in MWh and the grid emissions factor is
        # 18 kg CO2 per MWh (18 g/kWh).
        co2_grid = flows["Electricity"] * 18
        total_co2 = co2_leakage + co2_grid
        return {
            "kg_co2_per_kg_h2": total_co2 / flows["H2"],
            "total_kg_co2": total_co2,
        }
