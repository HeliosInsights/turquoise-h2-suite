"""Renewable-powered hydrogen supply block with simple optimiser."""
from dataclasses import dataclass
from typing import Sequence, Dict, Any

try:
    from scipy.optimize import minimize  # type: ignore
except Exception:  # pragma: no cover - scipy unavailable
    minimize = None

from supply import SupplyBlock
from .thermal_battery import BatteryTES


@dataclass
class RenewableParams:
    elec_per_kg: float = 50  # kWh/kg H2 for electrolysis
    pv_capex_per_kw: float = 1000
    wind_capex_per_kw: float = 1500
    battery_capex_per_mwh: float = 400000
    fixed_opex_frac: float = 0.03


class RenewableSupply(SupplyBlock):
    """Size PV/wind and storage to meet demand using optimisation."""

    def __init__(
        self,
        demand_profile: Sequence[float],
        solar_cf: Sequence[float],
        wind_cf: Sequence[float],
        params: RenewableParams | None = None,
    ):
        super().__init__(demand_profile)
        self.solar_cf = list(solar_cf)
        self.wind_cf = list(wind_cf)
        self.params = params or RenewableParams()
        self.pv_mw = 0.0
        self.wind_mw = 0.0
        self.battery = BatteryTES(0.0, capex_per_mwh=self.params.battery_capex_per_mwh)
        self._size_system()

    def _simulate(self, pv_mw: float, wind_mw: float, batt_mwh: float) -> float:
        battery = BatteryTES(batt_mwh)
        total_deficit = 0.0
        demand_mwh = [d * self.params.elec_per_kg / 1000 for d in self.demand]
        for d, scf, wcf in zip(demand_mwh, self.solar_cf, self.wind_cf):
            generation = pv_mw * scf + wind_mw * wcf
            if generation >= d:
                battery.charge(generation - d)
            else:
                need = d - generation
                remain = battery.discharge(need)
                total_deficit += remain
        return total_deficit

    def _objective(self, x):
        pv, wind, batt = x
        deficit = self._simulate(pv, wind, batt)
        capex = (
            pv * 1000 * self.params.pv_capex_per_kw
            + wind * 1000 * self.params.wind_capex_per_kw
            + batt * self.params.battery_capex_per_mwh
        )
        penalty = deficit * 1e6  # large penalty for unmet demand
        return capex + penalty

    def _size_system(self):
        if minimize is not None:
            res = minimize(
                self._objective,
                x0=[1.0, 1.0, 1.0],
                bounds=[(0, None), (0, None), (0, None)],
            )
            pv, wind, batt = res.x
        else:  # crude heuristic if scipy not available
            pv = max(self.demand) * self.params.elec_per_kg / 1000 / max(self.solar_cf or [1])
            wind = 0.0
            batt = 0.0
        self.pv_mw = float(pv)
        self.wind_mw = float(wind)
        self.battery = BatteryTES(float(batt), capex_per_mwh=self.params.battery_capex_per_mwh)

    def mass_energy(self) -> Dict[str, float]:
        return {"H2": float(sum(self.demand))}

    def capex_opex(self) -> Dict[str, Any]:
        capex = (
            self.pv_mw * 1000 * self.params.pv_capex_per_kw
            + self.wind_mw * 1000 * self.params.wind_capex_per_kw
            + self.battery.capacity_mwh * self.params.battery_capex_per_mwh
        )
        annualised = 0.1 * capex
        lcoh = annualised / self.mass_energy()["H2"]
        return {"capex": capex, "lcoh": lcoh}

    def lca(self) -> Dict[str, float]:
        return {"kg_co2_per_kg_h2": 0.0, "total_kg_co2": 0.0}
