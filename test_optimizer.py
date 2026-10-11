from services.data_generator import generate_demo
from services.bus_optimizer import optimize
def test_fixed_fleet_and_unique_assignments():
    r=optimize(generate_demo()); assert r["fleet_count_before"]==r["fleet_count_after"]==12 and r["fleet_invariant"]
    assert len({m["bus_id"] for m in r["moves"]})==len(r["moves"])
def test_donor_minimum_service_and_tradeoff():
    r=optimize(generate_demo())
    assert all(n>=1 for n in r["recommended_allocation"].values())
    assert all(m["source_stop"]!=m["destination_stop"] and m["source_service_loss_passengers"]>=0 and m["destination_improvement_passengers"]>0 for m in r["moves"])
def test_impossible_travel_not_counted():
    assert all(m["travel_minutes"]<=5 for m in optimize(generate_demo(),horizon_minutes=5)["moves"])
