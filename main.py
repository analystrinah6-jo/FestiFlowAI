"""FastAPI entry point for CrowdRipple AI."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from services.data_generator import generate_demo
from services.disruption_simulator import apply_scenario
from services.crowd_predictor import predict
from services.bus_optimizer import optimize
from services.metrics import available_buses, fleet_invariant
from database.db import save_run, recent_runs
import random

app=FastAPI(title="CrowdRipple AI",version="1.0.0",description="Synthetic festival crowd prediction and fixed-fleet redistribution demo")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:8501","http://127.0.0.1:8501"],allow_methods=["GET","POST"],allow_headers=["*"])
baseline_state=generate_demo(); current_state=baseline_state
class ScenarioRequest(BaseModel):
    broken_bus: str|None=None
    traffic: str=Field("normal",pattern="^(normal|moderate|heavy|severe)$")
    weather: str=Field("normal",pattern="^(normal|light rain|heavy rain)$")
    crowd_surge: float=Field(1.0,ge=.5,le=3.0)
    event_end_minutes: int=Field(120,ge=0,le=720)
    closed_stop: str|None=None
class RecommendRequest(BaseModel):
    horizon_minutes: int=Field(30,ge=5,le=60)
    minimum_buses_per_open_stop: int=Field(1,ge=0,le=12)
class NewScenarioRequest(BaseModel):
    seed: int|None=None
    capacity: int=Field(55,ge=20,le=100)
@app.get("/")
def root(): return {"project":"CrowdRipple AI","status":"operational","api_version":app.version,"data":"synthetic demo only","docs":"/docs","fleet_size":len(current_state["buses"])}
@app.get("/health")
def health(): return {"status":"healthy","fleet_invariant":fleet_invariant(current_state)}
@app.get("/stops")
def stops(): return {"data_label":current_state["generated_label"],"stops":current_state["stops"]}
@app.get("/buses")
def buses(): return {"fleet_count":len(current_state["buses"]),"available_count":available_buses(current_state),"buses":current_state["buses"]}
@app.get("/predict")
def get_prediction():
    result=predict(current_state); save_run(current_state.get("scenario",{}),current_state,result)
    return result
@app.post("/simulate")
def simulate(request: ScenarioRequest):
    global current_state
    try: current_state=apply_scenario(baseline_state,traffic=request.traffic,weather=request.weather,surge=request.crowd_surge,broken_bus=request.broken_bus,closed_stop=request.closed_stop,event_end_minutes=request.event_end_minutes)
    except ValueError as e: raise HTTPException(422,str(e)) from e
    prediction=predict(current_state); run_id=save_run(request.model_dump(),current_state,prediction)
    return {"run_id":run_id,"scenario":current_state["scenario"],"state":current_state,"prediction":prediction,"fleet_invariant":fleet_invariant(current_state)}
@app.post("/recommend")
def recommend(request: RecommendRequest):
    try: result=optimize(current_state,request.horizon_minutes,request.minimum_buses_per_open_stop)
    except (ValueError,KeyError) as e: raise HTTPException(422,str(e)) from e
    save_run({"recommendation":request.model_dump()},current_state,predict(current_state),result)
    return result
@app.get("/history")
def history(limit: int=20):
    if not 1<=limit<=100: raise HTTPException(422,"limit must be between 1 and 100")
    return {"runs":recent_runs(limit)}
@app.post("/scenario/new")
def new_scenario(request: NewScenarioRequest):
    global baseline_state,current_state
    seed=request.seed if request.seed is not None else random.SystemRandom().randint(0,2**31-1)
    try: baseline_state=generate_demo(seed,request.capacity)
    except ValueError as e: raise HTTPException(422,str(e)) from e
    current_state=baseline_state
    prediction=predict(current_state); run_id=save_run({"seed":seed,"capacity":request.capacity},current_state,prediction)
    return {"run_id":run_id,"seed":seed,"state":current_state,"prediction":prediction}
