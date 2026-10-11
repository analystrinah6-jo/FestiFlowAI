from services.data_generator import generate_demo
from services.crowd_predictor import predict, queue_balance
def test_queue_balance_never_negative(): assert queue_balance(2,1,9)==0
def test_prediction_horizons_recursive_and_ordered():
    p=predict(generate_demo(),(15,30,60)); assert p["horizons"]==[15,30,60]
    for data in p["stops"].values():
        assert [x["minutes"] for x in data["estimates"]]==[15,30,60]
        assert all(x["queue"]>=0 for x in data["estimates"])
def test_passenger_accounting_queue_balance(): assert queue_balance(100,50,40)==110
