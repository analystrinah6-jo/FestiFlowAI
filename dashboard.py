"""Streamlit dashboard; business logic is provided only by FastAPI."""
import requests, streamlit as st, pandas as pd, plotly.express as px
st.set_page_config(page_title="CrowdRipple AI",page_icon="🌊",layout="wide")
API=st.sidebar.text_input("FastAPI base URL","http://127.0.0.1:8000").rstrip("/")
st.markdown("<div style='background:#7f1d1d;color:white;padding:10px 16px;border-radius:8px;text-align:center;font-weight:700'>SIMULATED DATA — NOT LIVE TRANSPORT DATA</div>",unsafe_allow_html=True)
st.title("🌊 CrowdRipple AI")
st.caption("Predictive crowd and fixed-fleet bus redistribution · Festival operations demo")
def api(path,method="get",**kwargs):
    try:
        response=getattr(requests,method)(API+path,timeout=4,**kwargs); response.raise_for_status(); return response.json()
    except requests.RequestException as exc:
        st.error(f"Cannot reach FastAPI at {API}. Start it with `uvicorn main:app --reload`. Details: {exc}"); st.stop()
if st.sidebar.button("Generate new demo scenario",use_container_width=True): api("/scenario/new","post",json={})
with st.sidebar.form("scenario"):
    st.subheader("Disruption scenario")
    buses_data=api("/buses")["buses"]
    broken=st.selectbox("Breakdown",["None"]+[b["id"] for b in buses_data])
    traffic=st.selectbox("Traffic",["normal","moderate","heavy","severe"])
    weather=st.selectbox("Weather",["normal","light rain","heavy rain"])
    surge=st.slider("Crowd surge multiplier",.5,3.0,1.0,.1)
    stops_data=api("/stops")["stops"]
    closure=st.selectbox("Temporary stop closure",["None"]+[s["name"] for s in stops_data])
    event_end=st.slider("Minutes until event end",0,720,120,15)
    apply=st.form_submit_button("Apply scenario",use_container_width=True)
if apply:
    api("/simulate","post",json={"broken_bus":None if broken=="None" else broken,"traffic":traffic,"weather":weather,"crowd_surge":surge,"closed_stop":None if closure=="None" else closure,"event_end_minutes":event_end})
state=api("/stops"); bdata=api("/buses"); prediction=api("/predict")
total_queue=sum(s["queue"] for s in state["stops"]); high=sum(any(e["risk"]=="HIGH" for e in prediction["stops"][s["name"]]["estimates"]) for s in state["stops"])
c1,c2,c3,c4=st.columns(4)
c1.metric("Festival attendance assumption","40,000",help="Assumed overall attendance; only 28% modeled as bus users.")
c2.metric("Waiting passengers",f"{total_queue:,}")
c3.metric("Available buses",f"{bdata['available_count']} / {bdata['fleet_count']}")
c4.metric("Stops with high simulated risk",str(high))
st.subheader("Predicted queue by stop")
rows=[]
for stop,info in prediction["stops"].items():
    for e in info["estimates"]: rows.append({"Stop":stop,"Horizon (minutes)":e["minutes"],"Predicted queue":e["queue"],"Risk":e["risk"]})
df=pd.DataFrame(rows)
left,right=st.columns([1.4,1])
left.plotly_chart(px.line(df,x="Horizon (minutes)",y="Predicted queue",color="Stop",markers=True,title="Recursive queue estimates"),use_container_width=True)
right.plotly_chart(px.bar(pd.DataFrame(state["stops"]),x="name",y="queue",color="open",title="Current waiting queue"),use_container_width=True)
st.subheader("Bus allocation overview")
allocation=pd.DataFrame([{"Stop":s["name"],"Buses":sum(b["location"]==s["name"] and b["status"]=="available" for b in bdata["buses"]),"Queue":s["queue"],"Open":s["open"]} for s in state["stops"]])
st.dataframe(allocation,use_container_width=True,hide_index=True)
if st.button("Run redistribution optimizer",type="primary"):
    rec=api("/recommend","post",json={"horizon_minutes":30,"minimum_buses_per_open_stop":1}); st.session_state["recommendation"]=rec
if "recommendation" in st.session_state:
    rec=st.session_state["recommendation"]; st.subheader("Redistribution recommendations")
    st.caption(f"Fleet before: {rec['fleet_count_before']} · Fleet after: {rec['fleet_count_after']} · {rec['message']}")
    st.write("Allocation before → after")
    before=pd.DataFrame([{"Stop":k,"Before":v,"After":rec["recommended_allocation"].get(k,v)} for k,v in rec["original_allocation"].items()]); st.dataframe(before,use_container_width=True,hide_index=True)
    if rec["moves"]:
        for m in rec["moves"]:
            st.info(f"{m['explanation']} Destination service improvement: {m['destination_improvement_passengers']} passengers; source service loss / added unmet demand: {m['source_service_loss_passengers']} passengers. Estimated wait improvement: {m['estimated_wait_improvement_minutes']} minutes.")
        st.plotly_chart(px.bar(pd.DataFrame(rec["moves"]),x="bus_id",y=["destination_improvement_passengers","source_service_loss_passengers"],barmode="group",title="Destination improvement vs source service loss"),use_container_width=True)
    st.caption(rec["limitations"])
st.caption("Traffic and weather multipliers are illustrative scenario inputs. Risk thresholds are simulation thresholds, not certified safety limits. No real transport or CCTV data is connected.")
