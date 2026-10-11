"""Transparent recursive queue-balance predictor (5-minute steps)."""
import math

def predict(state: dict, horizons=(15,30,60), capacity_threshold=0.85):
    horizon_max = max(horizons)
    output = {s["name"]: {"queue":s["queue"], "estimates":[]} for s in state["stops"]}
    fleet_by_stop = {s["name"]: sum(1 for b in state["buses"] if b["location"] == s["name"] and b["status"] == "available") for s in state["stops"]}
    traffic = state.get("traffic_delay_multiplier", 1)
    for stop in state["stops"]:
        name=stop["name"]; q=float(stop["queue"]); available=fleet_by_stop[name]; cap=sum(b["capacity"] for b in state["buses"] if b["location"]==name and b["status"]=="available")
        for minute in range(5, horizon_max+1, 5):
            # Arrivals ramp modestly toward event end; hourly timing is an explicit demo assumption.
            ramp = 1.12 if minute >= state.get("scenario",{}).get("event_end_minutes",120)-30 else 1.0
            arrivals=stop["arrival_rate_per_5m"]*ramp
            boarding=min(q+arrivals, available*stop.get("boarding_per_bus_per_5m",18)/max(1,traffic))
            q=max(0, q+arrivals-boarding)
            if minute in horizons:
                wait=round(q/max(1, stop["arrival_rate_per_5m"] + 1)*5,1)
                risk="HIGH" if (cap and q >= cap*capacity_threshold) or q >= 1200 else "MEDIUM" if (cap and q >= cap*.5) or q >= 500 else "LOW"
                output[name]["estimates"].append({"minutes":minute,"queue":int(round(q)),"expected_arrivals":int(round(arrivals*minute/5)),"expected_boarding":int(round(boarding*minute/5)),"estimated_wait_minutes":wait,"risk":risk,"risk_threshold_note":"Simulation thresholds; not certified safety limits"})
    return {"horizons":list(horizons),"stops":output,"method":"Recursive 5-minute queue balance: max(0, queue + arrivals - boarding)","data_label":state["generated_label"]}

def queue_balance(current_queue, expected_arrivals, expected_boarding):
    return max(0, current_queue + expected_arrivals - expected_boarding)
