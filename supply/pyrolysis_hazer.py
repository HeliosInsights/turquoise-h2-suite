from dataclasses import dataclass
from typing import Dict, Any, Sequence
from statistics import mean

from .base import SupplyBlock
from core import enthalpy
from .electrolysis import elec_price_default


@dataclass
class HazerParams:
    """Key parameters for a Hazer-style methane pyrolysis plant."""
    ch4_per_h2: float = 3.8  # kg CH4 per kg H2
    comp_elec_per_h2: float = 0.58  # MWh per t H2 (PSA + compression)
    preheat_temp_c: float = 400.0
    reactor_temp_c: float = 950.0
    tailgas_fraction: float = 0.15  # fraction of CH4 feed as tail-gas
    tailgas_utilisation: float = 0.9
    catalyst_makeup_fe_per_h2: float = 0.8  # kg Fe per kg H2
    catalyst_price: float = 0.2  # USD per kg Fe
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
        """Mass and energy flows based on simple enthalpy balance."""
        h2_flow = list(self.demand)
        total_h2 = float(sum(h2_flow))
        ch4_mass = total_h2 * self.params.ch4_per_h2
        ch4_mol = enthalpy.mass_to_mol("CH4", ch4_mass)

        # Heat duties
        heat_pre = enthalpy.sensible_enthalpy(
            "CH4", 25.0, self.params.reactor_temp_c
        ) * ch4_mol
        heat_rxn = enthalpy.reaction_heat_per_mol_h2() * enthalpy.mass_to_mol(
            "H2", total_h2
        )
        heat_cool = enthalpy.sensible_enthalpy(
            "CH4", self.params.reactor_temp_c, 70.0
        ) * ch4_mol
        tailgas_mass = ch4_mass * self.params.tailgas_fraction
        tailgas_heat = (
            enthalpy.lhv("CH4")
            * 1e3
            * tailgas_mass
            * self.params.tailgas_utilisation
        )
        net_heat_kJ = max(0.0, heat_pre + heat_rxn - heat_cool - tailgas_heat)
        heater_mwh = net_heat_kJ / 3.6e6

        comp_elec = self.params.comp_elec_per_h2 * total_h2 / 1000
        electricity = comp_elec + heater_mwh

        return {
            "H2": total_h2,
            "CH4": ch4_mass,
            "Electricity": electricity,
            "CatalystFe": total_h2 * self.params.catalyst_makeup_fe_per_h2,
        }

    def capex_opex(self) -> Dict[str, Any]:
        avg_rate = mean(self.demand)  # kg/h
        size_tpd = avg_rate * 24 / 1000  # t H2/day
        capex = size_tpd * self.params.capex_per_tpd
        flows = self.mass_energy()
        graphite_rev = flows["H2"] * self.params.graphite_per_h2 * self.params.graphite_price
        fuel_cost = flows["CH4"] * self.params.ng_price
        power_cost = flows["Electricity"] * 1000 * elec_price_default
        catalyst_cost = flows["CatalystFe"] * self.params.catalyst_price
        annualised = 0.1 * capex  # 10 % capital recovery as placeholder
        lcoh = (
            annualised + fuel_cost + power_cost + catalyst_cost - graphite_rev
        ) / flows["H2"]
        return {
            "capex": capex,
            "fuel_cost": fuel_cost,
            "power_cost": power_cost,
            "catalyst_cost": catalyst_cost,
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

    def byproducts(self) -> Dict[str, float]:
        """Return mass flows of graphite, tail-gas and catalyst."""
        h2_total = float(sum(self.demand))
        return {
            "graphite": h2_total * self.params.graphite_per_h2,
            "tail_gas": h2_total * 0.15,  # kg per kg H2 from PSA slip-stream
            "catalyst": h2_total * 0.8,   # kg Fe ore make-up per kg H2
        }
