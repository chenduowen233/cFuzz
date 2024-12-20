import base64
import httpx
import uuid
import re
import os
import json
import pymongo
from utils.config import mongodb_cli
from generator import generate_request

db = pymongo.MongoClient(mongodb_cli)["fuzz"]
db_reqs = db["request"]
db_reps = db["response"]
db_diff = db["diff"]

# 目标服务器信息
HOST = "tbg.iinfinity.cn"
PORT = 443

def placeholder(packet, token):
    """用于占位符替换的函数，可以扩展"""
    packet["X-Token"] = token
    return packet

def store_request(token, request_data):
    """存储请求数据到 MongoDB"""
    db_reqs.update_one(
        {"X-Token": token},
        {"$set": {"client": request_data, "host": HOST}},
        upsert=True
    )
    print(f"[+] Logged request with X-Token: {token}")


def store_response(token, response_data):
    """存储响应数据到 MongoDB"""
    response_len = len(response_data)
    db_reps.update_one(
        {"X-Token": token},
        {"$set": {"client": response_data, "client_len": response_len}},
        upsert=True
    )
    print(f"[+] Logged response for X-Token: {token}")

async def send_request():
    """生成请求、发送 HTTP/2 请求，并存储结果到数据库"""
    try:
        # 使用 httpx 客户端
        async with httpx.AsyncClient(http2=True) as client:
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
            response = await client.request(
                method=headers[":method"],
                url=f"https://{HOST}:{PORT}{headers[':path']}",
                headers=headers,
                content=body.encode('utf-8')
            )

            # 解析响应数据
            response_data = await response.text()
            print(f"\nResponse Status: {response.status_code}")
            print("Response Headers:")
            for header, value in response.headers.items():
                print(f"{header}: {value}")
            print("\nResponse Data:")
            print(response_data)
            request_client = placeholder({"headers": headers, "body": body}, token)
            store_request(token, request_client)
            store_response(token, response_data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    for i in range(5):  # 发送 5 次请求
        print(f"\n=== Sending request {i + 1} ===")
        loop.run_until_complete(send_request())
