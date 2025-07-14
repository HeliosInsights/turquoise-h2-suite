class GraphiteLedger:
    """Simple ledger for allocating Hazer graphite."""

    def __init__(self, flow_kg_h: float):
        self.flow = float(flow_kg_h)
        self.to_fines = 0.0
        self.to_electrodes = 0.0
        self.to_sale = self.flow

    def allocate(self, eaf_fines: float = 20.0, electrodes: float = 1.8) -> None:
        """Allocate graphite to internal uses then sale."""
        self.to_fines = eaf_fines
        self.to_electrodes = electrodes
        self.to_sale = max(0.0, self.flow - eaf_fines - electrodes)
