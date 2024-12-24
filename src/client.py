import base64
import httpx
import uuid
import re
import os
import json
import pymongo
#from utils.config import mongodb_cli
from generator import generate_request
from collections.abc import MutableSet

# 替换成你的 MongoDB 信息
uri = "mongodb://user:Pwd_SH0U1D_NO7_bE_Too_W33k@8.219.161.121:2777/fuzz"
db = pymongo.MongoClient(uri)["fuzz"]
db_reqs = db["request"]
db_reps = db["response"]
db_diff = db["diff"]
# 目标服务器信息
HOST = "tbg.iinfinity.cn"

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
        async with httpx.AsyncClient(http2=True, verify=False) as client:
            # 从 generator 获取请求头和体
            headers, body = generate_request()
            # 提取伪标头（:method, :path, :scheme）并移除它们
            method = headers.pop(":method")
            path = headers.pop(":path")
            scheme = headers.pop(":scheme")

            # 生成随机 token 并添加到请求头
            token = os.urandom(8).hex()
            headers["X-Token"] = token

            # 打印生成的请求
            print(f"\nSending HTTP/2 Request:")
            print(f"Headers: {headers}")
            print(f"Body: {body}")

            # 发送请求
            response = await client.request(
                method=method,
                url=f"https://{HOST}/{path}",
                headers=headers,
                content=body.encode('utf-8')
            )

            # 解析响应数据
            #print(response)  # 应该输出<class 'method'>
            response_data = response.text
            print(f"\nResponse Status: {response.status_code}")
            print("Response Headers:")
            for header, value in response.headers.items():
                print(f"{header}: {value}")
            request_client = placeholder({"headers": headers, "body": body}, token)
            print(request_client)
            print(response_data)
            store_request(token, request_client)
            store_response(token, response_data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    for i in range(10):  # 发送 5 次请求
        print(f"\n=== Sending request {i + 1} ===")
        loop.run_until_complete(send_request())
