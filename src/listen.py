from flask import Flask, request
from scapy.all import sniff, TCP, Raw
import re
import pymongo
import pyshark
from utils.config import mongodb_cli

app = Flask(__name__)

db = pymongo.MongoClient(mongodb_cli)["fuzz"]
db_reqs = db["request"]
db_reps = db["response"]
db_diff = db["diff"]

# 提取 HTTP 请求中的 token
# 提取 Token 的函数
def extract_token(data):
    match = re.search(r'X-Token: ([a-zA-Z0-9]+)', data)
    return match.group(1) if match else None

# 处理捕获的数据包
def process_packet(packet):
    try:
        # 检查是否包含 HTTP/2 数据帧
        if 'http2' in packet:
            http2_layer = packet.http2

            # 提取请求或响应头部
            headers = http2_layer.get_field('header')
            if headers:
                token = extract_token(headers)
                if token:
                    print(f"Captured X-Token: {token}")

                    # 提取响应数据（如存在）
                    response = http2_layer.get_field('data') or ""
                    response_len = len(response)

                    # 更新 MongoDB 数据
                    db_reps.update_one(
                        {"X-Token": token},
                        {"$set": {"server": response, "server_len": response_len}},
                        upsert=True
                    )
                    print(f"Updated MongoDB for token {token}: Response length = {response_len}")
    except Exception as e:
        print(f"Error processing packet: {e}")

# 启动捕获函数
def start_sniffing(interface="eth0"):
    print("Starting HTTP/2 packet capture...")
    capture = pyshark.LiveCapture(interface=interface, display_filter="http2")
    for packet in capture:
        process_packet(packet)

if __name__ == "__main__":
    start_sniffing()
