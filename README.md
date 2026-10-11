# CrowdRipple AI – Predictive Crowd & Bus Redistribution System

An end-to-end synthetic-data MVP for festival crowd forecasting and fixed-fleet bus redistribution. It is decision-support software, not live transport monitoring or a dispatch system.

## What it models

- Six demo stops, exactly 12 bus records, 40,000 assumed attendees, and a 28% illustrative public-bus share.
- Reproducible default random seed `42`; each bus has configurable capacity (default 55).
- Current queues and five-minute arrival rates; recursive queue-balance estimates at 15, 30, and 60 minutes.
- Scenario controls for bus breakdown, traffic, weather, crowd surge, event end, and stop closure.
- A greedy fixed-fleet optimizer that checks donor minimum service, bus availability, and travel time against the selected horizon.
- Persistent run and prediction history in `data/crowdripple.sqlite3`.

All generated quantities are synthetic estimates. Traffic travel-time factors (normal 1.0, moderate 1.25, heavy 1.65, severe 2.2), weather travel factors (1.0/1.10/1.25), and weather demand factors (1.0/1.03/1.08) are illustrative assumptions supplied for scenario exploration. They are not established empirical relationships. A rain demand factor applies a mild increase as a deliberately visible modeling assumption, which operators should replace with local evidence. Risk thresholds are configurable in the predictor and are not certified safety limits.

Passenger queues follow `max(0, queue + arrivals - boarding)` at each five-minute step, so boarding removes passengers from the waiting queue and no step produces a negative queue. The optimizer is a transparent greedy heuristic; it does not model road-network interactions, bus duty rules, accessible capacity, or stochastic confidence intervals. Its queue deltas are capacity-based estimates.

## Windows setup

Open PowerShell in this directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the Python launcher `py` is unavailable, install Python 3.11 or newer and enable “Add Python to PATH”, then replace `py` with `python`.

## Run the API and dashboard

Terminal 1:

```powershell
cd C:\path\to\CrowdRippleAI
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger. Terminal 2:

```powershell
cd C:\path\to\CrowdRippleAI
.\.venv\Scripts\Activate.ps1
streamlit run dashboard.py
```

The dashboard uses HTTP requests to the API at `http://127.0.0.1:8000`; change the sidebar URL if needed. If the API is down, the dashboard presents a readable error.

## API quick checks

```powershell
Invoke-RestMethod http://127.0.0.1:8000/
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/stops
Invoke-RestMethod http://127.0.0.1:8000/buses
Invoke-RestMethod http://127.0.0.1:8000/predict
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/simulate -ContentType 'application/json' -Body '{"traffic":"heavy","weather":"light rain","crowd_surge":1.3,"event_end_minutes":90,"broken_bus":"B01"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/recommend -ContentType 'application/json' -Body '{"horizon_minutes":30,"minimum_buses_per_open_stop":1}'
Invoke-RestMethod 'http://127.0.0.1:8000/history?limit=10'
```

`POST /scenario/new` explicitly generates a new seed (or accepts a fixed `seed` and `capacity`). Server reloads do not delete the database. All endpoints are also available interactively in Swagger.

## Tests and fleet verification

```powershell
pytest -q
```

Verification report: default state has 12 unique IDs (`B01`–`B12`). Scenario changes only update bus status or scenario fields; they do not add or remove bus records. The optimizer reports `fleet_count_before`, `fleet_count_after`, and `fleet_invariant` and only returns moves for existing available bus IDs. The test suite asserts the fixed fleet, unique recommended bus IDs, donor minimums, closure behavior, and travel-horizon feasibility. Fleet status can be checked at `/health`.

## Project layout

```text
main.py                         FastAPI app
dashboard.py                    Streamlit UI calling the API
services/                       Synthetic generation, prediction, disruption, optimization
database/db.py                  SQLite run-history storage
data/                           Persistent SQLite database is created here
tests/                          Pytest suite
```
