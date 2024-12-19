import pymongo
from utils.config import mongodb_cli

db = pymongo.MongoClient(mongodb_cli)["fuzz"]
db_reqs = db["request"]
db_reps = db["response"]
db_diff = db["diff"]

def compare_requests_and_responses():
    for entry in db_reqs.find():
        token = entry["token"]
        request_data = entry["request"]
        response_data = entry["response"]

        # 查找源站响应
        nginx_entry = db_reps.find_one({"token": token})
        if nginx_entry:
            print(f"Token: {token}")
            print("Client Request:", request_data)
            print("Nginx Request:", nginx_entry["request"])
            print("Client Response:", response_data)
            print("Nginx Response:", nginx_entry["response"])
            print("Differences:", compare_data(entry, nginx_entry))

def compare_data(client_entry, nginx_entry):
    # 简单对比实现，可根据需求增加差异分析的深度
    differences = {}
    if client_entry["request"] != nginx_entry["request"]:
        differences["request"] = "Requests are different"
    if client_entry["response"] != nginx_entry["response"]:
        differences["response"] = "Responses are different"
    return differences

compare_requests_and_responses()
