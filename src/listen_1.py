# import socket
# import re
# import pymongo
# import pyshark  # 用于抓取网络流量
# from utils.config import mongodb_cli
#
# db = pymongo.MongoClient(mongodb_cli)["fuzz"]
# db_reqs = db["request"]
# db_reps = db["response"]
# db_diff = db["diff"]
#
# # 网络抓包接口和端口配置
# INTERFACE = "eth0"  # 替换为源站服务器的网络接口名称
# PORT = "80"  # HTTP 默认端口，抓取 HTTP 流量
#
#
# def extract_x_token(data):
#     """从 HTTP 请求头或响应中提取 X-Token"""
#     match = re.search(r'X-Token: ([a-zA-Z0-9]+)', data)
#     if match:
#         return match.group(1)
#     return None
#
#
# def store_request(token, request_data):
#     """存储请求数据到 MongoDB"""
#     db_reqs.update_one(
#         {"X-Token": token},
#         {"$set": {"server": request_data}},
#         upsert=True
#     )
#     print(f"[+] Logged request with X-Token: {token}")
#
#
# def store_response(token, response_data):
#     """存储响应数据到 MongoDB"""
#     response_len = len(response_data)
#     db_reps.update_one(
#         {"X-Token": token},
#         {"$set": {"server": response_data, "server_len": response_len}},
#         upsert=True
#     )
#     print(f"[+] Logged response for X-Token: {token}")
#
#
# def process_packet(packet):
#     """解析流量包，提取 HTTP 请求或响应"""
#     try:
#         if "HTTP" in packet:
#             # 提取 HTTP 数据
#             http_layer = packet.http
#             data = str(http_layer)
#
#             # 从数据中提取 X-Token
#             token = extract_x_token(data)
#             if token:
#                 if hasattr(http_layer, "request_line"):  # 请求
#                     store_request(token, data)
#                 elif hasattr(http_layer, "response_line"):  # 响应
#                     store_response(token, data)
#     except Exception as e:
#         print(f"Error processing packet: {e}")
#
#
# def main():
#     print(f"Starting packet capture on interface {INTERFACE} for port {PORT}...")
#
#     # 使用 pyshark 抓包
#     capture = pyshark.LiveCapture(interface=INTERFACE, bpf_filter=f"tcp port {PORT}")
#     for packet in capture.sniff_continuously():
#         process_packet(packet)
#
#
# if __name__ == "__main__":
#     main()
from scapy.all import sniff
from scapy.layers.inet import TCP
from scapy.layers.http import HTTPRequest, HTTPResponse
import re
import pymongo
from utils.config import mongodb_cli

db = pymongo.MongoClient(mongodb_cli)["fuzz"]
db_reqs = db["request"]
db_reps = db["response"]
db_diff = db["diff"]

# 网络抓包接口和端口配置
INTERFACE = "eth0"  # 替换为源站服务器的网络接口名称
PORT = 80  # HTTP 默认端口，抓取 HTTP 流量


def extract_x_token(data):
    """从 HTTP 请求头或响应中提取 X-Token"""
    match = re.search(r'X-Token: ([a-zA-Z0-9]+)', data)
    if match:
        return match.group(1)
    return None


def store_request(token, request_data):
    """存储请求数据到 MongoDB"""
    db_reqs.update_one(
        {"X-Token": token},
        {"$set": {"server": request_data}},
        upsert=True
    )
    print(f"[+] Logged request with X-Token: {token}")


def store_response(token, response_data):
    """存储响应数据到 MongoDB"""
    response_len = len(response_data)
    db_reps.update_one(
        {"X-Token": token},
        {"$set": {"server": response_data, "server_len": response_len}},
        upsert=True
    )
    print(f"[+] Logged response for X-Token: {token}")


def process_packet(packet):
    """解析流量包，提取 HTTP 请求或响应"""
    try:
        if packet.haslayer(TCP) and (packet.haslayer(HTTPRequest) or packet.haslayer(HTTPResponse)):
            # 检查是否是 HTTP 请求
            if packet.haslayer(HTTPRequest):
                http_request = packet[HTTPRequest]
                print(http_request)
                data = bytes(http_request).decode(errors="ignore")
                token = extract_x_token(data)
                if token:
                    store_request(token, data)

            # 检查是否是 HTTP 响应
            elif packet.haslayer(HTTPResponse):
                http_response = packet[HTTPResponse]
                print(http_response)
                data = bytes(http_response).decode(errors="ignore")
                token = extract_x_token(data)
                if token:
                    store_response(token, data)
    except Exception as e:
        print(f"Error processing packet: {e}")


def main():
    print(f"Starting packet capture on interface {INTERFACE} for port {PORT}...")

    # 使用 scapy 抓包
    sniff(
        iface=INTERFACE,
        filter=f"tcp port {PORT}",
        prn=process_packet,
        store=False
    )


if __name__ == "__main__":
    main()
