def available_buses(state): return sum(b["status"]=="available" for b in state["buses"])
def fleet_invariant(state): return len(state["buses"]) == 12 and len({b["id"] for b in state["buses"]}) == 12
