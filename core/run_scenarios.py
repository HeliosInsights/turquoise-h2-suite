"""Run H2 supply scenarios configured by a YAML file."""
import sys
from typing import Sequence

import yaml

from supply import (
    HazerSupply,
    ElectrolysisSupply,
    HazerParams,
    ElectrolysisParams,
    elec_price_default,
)


SUPPLY_CLASSES = {
    "hazer": HazerSupply,
    "electrolysis": ElectrolysisSupply,
}


def build_supply(demand: Sequence[float], cfg: dict):
    """Instantiate the requested supply block with parameters from cfg."""
    source = cfg.get("H2_source", "hazer")
    if source not in SUPPLY_CLASSES:
        raise ValueError(f"Unknown H2_source '{source}'")

    if source == "hazer":
        params = HazerParams()
        if "graphite_price" in cfg:
            params.graphite_price = cfg["graphite_price"]
        if "ng_price" in cfg:
            params.ng_price = cfg["ng_price"]
        return HazerSupply(demand, params)

    params = ElectrolysisParams()
    elec_price = cfg.get("elec_price", elec_price_default)
    return ElectrolysisSupply(demand, params, elec_price=elec_price)


def format_table(results: dict) -> str:
    max_key = max(len(k) for k in results)
    lines = ["Metric".ljust(max_key) + "  Value", "-" * (max_key + 7)]
    for k, v in results.items():
        if isinstance(v, float):
            val = f"{v:.3f}"
        else:
            val = str(v)
        lines.append(f"{k.ljust(max_key)}  {val}")
    return "\n".join(lines)


def main(path: str) -> None:
    with open(path) as f:
        cfg = yaml.safe_load(f)

    demand_tpd = float(cfg.get("h2_demand_tpd", 7.55))
    demand_profile = [demand_tpd * 1000 / 24] * 24

    supply = build_supply(demand_profile, cfg)
    results = {
        **supply.mass_energy(),
        **supply.capex_opex(),
        **supply.lca(),
    }

    print(format_table(results))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m core.run_scenarios <config.yaml>")
        raise SystemExit(1)
    main(sys.argv[1])
