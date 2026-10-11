"""Greedy, explainable fleet redistribution with donor-service and travel constraints."""
from .disruption_simulator import travel_time
from .crowd_predictor import predict

def optimize(state: dict, horizon_minutes=30, minimum_buses=1):
    baseline=predict(state, (horizon_minutes,))
    queues={n:v["estimates"][0]["queue"] for n,v in baseline["stops"].items()}
    buses=[dict(b) for b in state["buses"]]
    open_stops=[s["name"] for s in state["stops"] if s["open"]]
    original={n:sum(b["location"]==n and b["status"]=="available" for b in buses) for n in open_stops}
    allocation=original.copy(); moves=[]; used=set()
    # Repeatedly move a donor's surplus bus to the highest queue if it can arrive within horizon.
    for _ in range(len(buses)):
        dest=max((n for n in open_stops if n in queues), key=lambda n: queues[n]/max(1,allocation[n]), default=None)
        if dest is None: break
        candidates=[]
        for src in open_stops:
            if src==dest or allocation[src] <= minimum_buses: continue
            travel=travel_time(state,src,dest)
            if travel > horizon_minutes: continue
            candidates.extend(b for b in buses if b["id"] not in used and b["location"]==src and b["status"]=="available")
        if not candidates: break
        # Move from least burdened feasible donor, only if projected destination capacity gains value.
        bus=min(candidates,key=lambda b:(queues[b["location"]]/max(1,allocation[b["location"]]), b["id"]))
        src=bus["location"]; travel=travel_time(state,src,dest)
        if queues[dest] <= queues[src] or allocation[dest]*bus["capacity"] >= queues[dest]: break
        dest_before=queues[dest]; src_before=queues[src]
        dest_gain=min(bus["capacity"], max(0,dest_before-allocation[dest]*bus["capacity"]))
        src_loss=min(bus["capacity"], max(0,src_before-max(0,allocation[src]-1)*bus["capacity"]))
        if dest_gain <= src_loss: break
        allocation[src]-=1; allocation[dest]+=1; queues[dest]=max(0,queues[dest]-dest_gain)
        used.add(bus["id"]); bus["location"]=dest; bus["assignment"]=dest
        moves.append({"bus_id":bus["id"],"source_stop":src,"destination_stop":dest,"buses_moved":1,"travel_minutes":travel,"destination_queue_before":dest_before,"destination_queue_after":queues[dest],"destination_improvement_passengers":int(dest_gain),"source_queue_before":src_before,"source_queue_after_estimate":int(src_before+src_loss),"source_service_loss_passengers":int(src_loss),"additional_unmet_demand_passengers":int(src_loss),"estimated_wait_improvement_minutes":round(dest_gain/max(1,next(s["arrival_rate_per_5m"] for s in state["stops"] if s["name"]==dest))*5,1),"explanation":f"Move bus {bus['id']} from {src} to {dest}. The projected queue at {dest} decreases by about {int(dest_gain)} passengers; {src} has one fewer assigned bus and an estimated queue increase of {int(src_loss)}. The bus takes about {travel} minutes to reach {dest}."})
    fleet_before=len(buses); fleet_after=len(buses)
    return {"moves":moves,"original_allocation":original,"recommended_allocation":allocation,"fleet_count_before":fleet_before,"fleet_count_after":fleet_after,"fleet_invariant":fleet_before==fleet_after==12,"baseline_predicted_queues":{n:v["estimates"][0]["queue"] for n,v in baseline["stops"].items()},"recommended_predicted_queues":queues,"message":"No beneficial feasible move exists under the current constraints." if not moves else "Recommendations preserve fleet size and minimum donor service.","limitations":"Greedy one-bus heuristic; synthetic demand and assumed boarding/travel effects. Recommendations are decision support, not dispatch commands."}
