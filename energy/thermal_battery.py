"""Simple thermal energy storage model."""
from dataclasses import dataclass


@dataclass
class BatteryTES:
    """Basic thermal battery with simple charge/discharge accounting."""

    capacity_mwh: float
    charge_eff: float = 0.95
    discharge_eff: float = 0.95
    capex_per_mwh: float = 400000  # USD per MWh

    def __post_init__(self):
        self.soc = 0.0  # state of charge in MWh

    def charge(self, mwh: float) -> float:
        """Charge the battery and return unused energy."""
        actual = mwh * self.charge_eff
        space = self.capacity_mwh - self.soc
        charged = min(space, actual)
        self.soc += charged
        return mwh - charged / self.charge_eff

    def discharge(self, mwh: float) -> float:
        """Discharge the battery and return unmet demand."""
        available = self.soc * self.discharge_eff
        provided = min(mwh, available)
        self.soc -= provided / self.discharge_eff
        return mwh - provided

    def cost_summary(self) -> dict:
        """Capital cost summary for the battery."""
        return {"capex": self.capacity_mwh * self.capex_per_mwh}
