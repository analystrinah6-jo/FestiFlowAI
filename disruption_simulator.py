"""Scenario adjustments; multipliers are documented assumptions, not empirical facts."""
TRAFFIC_DELAY = {"normal": 1.0, "moderate": 1.25, "heavy": 1.65, "severe": 2.2}
WEATHER_DELAY = {"normal": 1.0, "light rain": 1.10, "heavy rain": 1.25}
WEATHER_DEMAND = {"normal": 1.0, "light rain": 1.03, "heavy rain": 1.08}

def apply_scenario(state: dict, traffic="normal", weather="normal", surge=1.0, broken_bus=None, closed_stop=None, event_end_minutes=120):
    if traffic not in TRAFFIC_DELAY: raise ValueError(f"traffic must be one of {', '.join(TRAFFIC_DELAY)}")
    if weather not in WEATHER_DELAY: raise ValueError(f"weather must be one of {', '.join(WEATHER_DELAY)}")
    if not 0.5 <= surge <= 3.0: raise ValueError("surge must be between 0.5 and 3.0")
    stops = [dict(s) for s in state["stops"]]
    buses = [dict(b) for b in state["buses"]]
    if closed_stop and closed_stop not in [s["name"] for s in stops]: raise ValueError("closed_stop is not a known stop")
    if broken_bus and broken_bus not in [b["id"] for b in buses]: raise ValueError("broken_bus is not a known bus")
    for s in stops:
        s["open"] = s["name"] != closed_stop
        s["arrival_rate_per_5m"] = int(round(s["arrival_rate_per_5m"] * surge * WEATHER_DEMAND[weather])) if s["open"] else 0
    for b in buses:
        if b["id"] == broken_bus:
            b["status"] = "broken"
            b["assignment"] = None
        elif b["status"] != "broken":
            b["status"] = "available"
    return {**state, "stops": stops, "buses": buses, "scenario": {"traffic":traffic,"weather":weather,"surge":surge,"broken_bus":broken_bus,"closed_stop":closed_stop,"event_end_minutes":event_end_minutes,"traffic_delay_multiplier":TRAFFIC_DELAY[traffic],"weather_delay_multiplier":WEATHER_DELAY[weather],"weather_demand_multiplier":WEATHER_DEMAND[weather]}, "traffic_delay_multiplier":TRAFFIC_DELAY[traffic]*WEATHER_DELAY[weather]}

def travel_time(state, source, destination):
    names = [s["name"] for s in state["stops"]]
    return int(round(state["travel_minutes"][names.index(source)][names.index(destination)] * state.get("traffic_delay_multiplier", 1.0)))
