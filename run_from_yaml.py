"""Run the steel plant model from a YAML configuration."""
from typing import Sequence

from core.steel_plant import run_steel_plant
from energy.traces import load_traces


def run_scenario(path: str):
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyYAML is required to load scenario files") from exc

    with open(path) as f:
        cfg = yaml.safe_load(f)

    demand: Sequence[float] = cfg.get("demand", [7550 / 24] * 24)
    supply_type = cfg.get("supply_type", "hazer").lower()

    if supply_type == "renewable":
        traces_file = cfg.get("traces_file")
        if not traces_file:
            raise ValueError("traces_file required for renewable supply")
        solar, wind = load_traces(traces_file)
        result = run_steel_plant(demand, supply_type="renewable", solar=solar, wind=wind)
    else:
        result = run_steel_plant(demand, supply_type=supply_type)
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python run_from_yaml.py scenario.yaml")
        raise SystemExit(1)
    res = run_scenario(sys.argv[1])
    print(res)
