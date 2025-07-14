"""Simple driver script demonstrating the Hazer supply block."""
from core.steel_plant import run_steel_plant
from typing import List
from supply import GraphiteLedger

if __name__ == "__main__":
    demand: List[float] = [7550 / 24] * 24
    ledger = GraphiteLedger(0.0)
    result = run_steel_plant(demand, supply_type="hazer", ledger=ledger)
    print(result)
