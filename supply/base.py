from abc import ABC, abstractmethod
from typing import Dict, Any


class SupplyBlock(ABC):
    """Abstract base class for hydrogen supply blocks."""

    def __init__(self, demand_profile):
        """Store hourly hydrogen demand in kg/h."""
        self.demand = demand_profile

    @abstractmethod
    def mass_energy(self) -> Dict[str, float]:
        """Return mass and energy flows for the supply."""
        raise NotImplementedError

    @abstractmethod
    def capex_opex(self) -> Dict[str, Any]:
        """Return capital and operating cost details."""
        raise NotImplementedError

    @abstractmethod
    def lca(self) -> Dict[str, float]:
        """Return lifecycle assessment metrics."""
        raise NotImplementedError

    @abstractmethod
    def byproducts(self) -> Dict[str, float]:
        """Return mass flows of key byproducts like graphite."""
        raise NotImplementedError
