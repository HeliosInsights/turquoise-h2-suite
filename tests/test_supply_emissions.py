import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from supply import HazerSupply, ElectrolysisSupply


def test_emissions_small_profile():
    demand = [1, 1, 1]  # kg/h over three hours

    hazer = HazerSupply(demand)
    hazer_lca = hazer.lca()
    assert hazer_lca["total_kg_co2"] == pytest.approx(0.30754, rel=1e-3)
    assert hazer_lca["kg_co2_per_kg_h2"] == pytest.approx(0.10251, rel=1e-3)

    electrolysis = ElectrolysisSupply(demand)
    elec_lca = electrolysis.lca()
    assert elec_lca["total_kg_co2"] == pytest.approx(2.7)
    assert elec_lca["kg_co2_per_kg_h2"] == pytest.approx(0.9)
