import base64
import requests
import uuid
import re
import os
import json
import pymongo
from hyper import HTTP20Connection
from utils.config import mongodb_cli
from generator import generate_request

db = pymongo.MongoClient(mongodb_cli)["fuzz"]
db_reqs = db["request"]
db_reps = db["response"]
db_diff = db["diff"]

# 目标服务器信息
HOST = "example.com"
PORT = 443


def placeholder(packet, token):
    """用于占位符替换的函数，可以扩展"""
    packet["X-Token"] = token
    return packet


def send_request():
    """生成请求、发送 HTTP/2 请求，并存储结果到数据库"""
    try:
        conn = HTTP20Connection(HOST, port=PORT, secure=True)

        # 从 generator 获取请求头和体
        headers, body = generate_request()

        # 生成随机 token 并添加到请求头
        token = os.urandom(8).hex()
        headers["X-Token"] = token

        # 打印生成的请求
        print(f"\nSending HTTP/2 Request:")
        print(f"Headers: {headers}")
        print(f"Body: {body}")

        # 发送请求
        stream_id = conn.request(headers[":method"], headers[":path"], body=body.encode('utf-8'), headers=headers)
        response = conn.get_response(stream_id)

        # 解析响应数据
        response_data = response.read().decode('utf-8')
        print(f"\nResponse Status: {response.status}")
        print("Response Headers:")
        for header, value in response.headers.items():
            print(f"{header}: {value}")
        print("\nResponse Data:")
        print(response_data)

        # 从响应中提取 X-Token（模拟场景）
        matched_tokens = re.findall(rf"{token}", response_data)
        if matched_tokens:
            request_client = placeholder({"headers": headers, "body": body}, token)
            request_server = base64.b64decode(matched_tokens[0]).decode('utf-8') if matched_tokens else None

            # 存入数据库
            db_reqs.insert_one({
                "X-Token": token,
                "host": HOST,
                "client": request_client,
                "server": request_server
            })
            print(f"Saved to database: X-Token = {token}")
        else:
            print("No matching X-Token found in response.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    for i in range(5):  # 发送 5 次请求
        print(f"\n=== Sending request {i + 1} ===")
        send_request()
