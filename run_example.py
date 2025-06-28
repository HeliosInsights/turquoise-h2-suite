"""Simple driver script demonstrating the Hazer supply block."""
from core.steel_plant import run_steel_plant
from typing import List

if __name__ == "__main__":
    demand: List[float] = [7550 / 24] * 24
    result = run_steel_plant(demand, supply_type="hazer")
    print(result)
