# turquoise-h2-suite

A prototype techno‑economic modelling toolkit for hydrogen‑based steelmaking and methane pyrolysis. The code is deliberately simple but shows how different hydrogen supply technologies can plug into a steel plant model.

## Packages

- **`supply`** – pluggable hydrogen supply blocks. Currently supports:
  - `HazerSupply` – methane pyrolysis based on the Hazer process.
  - `ElectrolysisSupply` – basic electrolytic hydrogen model.
- **`energy`** – renewable utilities including `BatteryTES` and
  `RenewableSupply` for PV/wind powered hydrogen.
- **`core`** – minimal steel plant wrapper that uses a supply block to calculate costs and emissions.

## Quick example

```python
from core.steel_plant import run_steel_plant

# hourly demand profile (kg H2/h)
demand = [7550 / 24] * 24  # 7.55 t/h averaged over a day

result = run_steel_plant(demand, supply_type='hazer')
print(result)
```

This returns a dictionary with total hydrogen produced, supply CAPEX, levelised cost of hydrogen and associated CO₂ emissions.


You can also run scenarios from a YAML file using `run_from_yaml.py`:

```bash
python run_from_yaml.py scenario.yml
```
=======
## Scenario runner

`core.run_scenarios` executes a supply block based on a YAML configuration and prints a table of key outputs.

```bash
python -m core.run_scenarios example_scenario.yaml
```

The provided `example_scenario.yaml` defines keys such as `H2_source`, `graphite_price`, energy prices and the graphite allocation fraction.


## Web demo

A small web server in `web/app.py` visualises outputs. Start it from the repo
root and open `http://localhost:8000` in a browser:

```bash
python web/app.py
```

Select a supply type and press *Run* to see the resulting costs and emissions.
