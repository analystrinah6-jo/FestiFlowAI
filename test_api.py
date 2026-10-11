from fastapi.testclient import TestClient
from main import app
client=TestClient(app)
def test_endpoints_and_validation():
    assert client.get("/").status_code==200
    assert len(client.get("/buses").json()["buses"])==12
    assert len(client.get("/stops").json()["stops"])==6
    assert client.get("/predict").json()["horizons"]==[15,30,60]
    assert client.post("/simulate",json={"traffic":"unreal"}).status_code==422
    assert client.post("/recommend",json={"horizon_minutes":1000}).status_code==422
    assert client.get("/health").json()["fleet_invariant"]
