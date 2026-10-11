import pytest
from services.data_generator import generate_demo
from services.disruption_simulator import apply_scenario,travel_time
def test_breakdown_makes_bus_unavailable(): assert next(b for b in apply_scenario(generate_demo(),broken_bus="B01")["buses"] if b["id"]=="B01")["status"]=="broken"
def test_traffic_delays_travel():
    base=generate_demo(); assert travel_time(apply_scenario(base,traffic="heavy"),"Main Stand A","Market Road")>travel_time(apply_scenario(base),"Main Stand A","Market Road")
def test_weather_changes_assumptions():
    base=generate_demo(); assert apply_scenario(base,weather="heavy rain")["stops"][0]["arrival_rate_per_5m"]>=base["stops"][0]["arrival_rate_per_5m"]
def test_closure_and_invalid_breakdown():
    assert not next(s for s in apply_scenario(generate_demo(),closed_stop="Market Road")["stops"] if s["name"]=="Market Road")["open"]
    with pytest.raises(ValueError): apply_scenario(generate_demo(),broken_bus="B99")
