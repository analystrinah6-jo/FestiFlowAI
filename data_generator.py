"""Deterministic synthetic festival and fleet data."""
from __future__ import annotations
import numpy as np

STOP_NAMES = ["Main Stand A", "Market Road", "Temple Gate", "East Junction", "River Road", "Hill View"]
FLEET_SIZE = 12
DEFAULT_SEED = 42

def generate_demo(seed: int = DEFAULT_SEED, capacity: int = 55) -> dict:
    if not 20 <= capacity <= 100:
        raise ValueError("capacity must be between 20 and 100")
    rng = np.random.default_rng(seed)
    # 40,000 attendance; model 28% as bus users, distributed unevenly by stop.
    weights = np.array([.43, .18, .15, .10, .08, .06])
    queues = np.rint(rng.multinomial(round(40000 * .28), weights) * rng.uniform(.035, .065, 6)).astype(int)
    # Scale to plausible current queue while preserving relative demand; this is a snapshot, not cumulative boarding.
    queues = np.maximum(queues, [600, 250, 180, 120, 90, 60])
    arrivals = np.rint(np.array([115, 55, 45, 35, 28, 20]) * rng.uniform(.85, 1.15, 6)).astype(int)
    allocation = [5, 2, 2, 1, 1, 1]
    buses = []
    for i in range(FLEET_SIZE):
        stop_idx = next((j for j, n in enumerate(allocation) if sum(b["location"] == STOP_NAMES[j] for b in buses) < n), 5)
        buses.append({"id": f"B{i+1:02d}", "location": STOP_NAMES[stop_idx], "status": "available", "capacity": capacity, "assignment": STOP_NAMES[stop_idx], "in_transit_to": None, "eta_minutes": 0})
    return {"seed": seed, "attendance": 40000, "bus_share": .28, "stops": [{"name": n, "queue": int(q), "arrival_rate_per_5m": int(a), "open": True} for n,q,a in zip(STOP_NAMES, queues, arrivals)], "buses": buses, "travel_minutes": [[0 if i==j else int(8+abs(i-j)*5+((i+j)%3)*2) for j in range(6)] for i in range(6)], "generated_label": "SYNTHETIC DEMO DATA — NOT LIVE TRANSPORT DATA"}
