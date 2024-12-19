import random
import string
import json

def random_path(length=8):
    """随机生成 URL 路径"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_headers():
    """随机生成 HTTP/2 请求头"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "curl/7.68.0",
        "HTTPie/2.5.0"
    ]
    headers = {
        ":authority": "example.com",
        ":scheme": "https",
        ":method": "POST",
        ":path": f"/random/{random_path()}?id={random.randint(1000, 9999)}",
        "user-agent": random.choice(user_agents),
        "content-type": random.choice(["application/json", "application/x-www-form-urlencoded"]),
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
    }
    # 额外随机的自定义 header
    for _ in range(random.randint(1, 3)):
        random_key = "x-custom-" + ''.join(random.choices(string.ascii_lowercase, k=5))
        random_value = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        headers[random_key] = random_value
    return headers


def random_json_body():
    """随机生成 JSON 请求体"""
    body = {}
    for _ in range(random.randint(2, 5)):
        key = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
        value = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(3, 10)))
        body[key] = value
    return json.dumps(body)


def random_form_body():
    """随机生成表单数据请求体"""
    body = []
    for _ in range(random.randint(2, 5)):
        key = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
        value = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(3, 10)))
        body.append(f"{key}={value}")
    return "&".join(body)


def random_body(content_type):
    """根据 content-type 随机生成请求体"""
    if content_type == "application/json":
        return random_json_body()
    elif content_type == "application/x-www-form-urlencoded":
        return random_form_body()
    return ""


def generate_request():
    """生成完整的 HTTP/2 请求，包括 headers 和 body"""
    headers = random_headers()
    body = random_body(headers["content-type"])
    return headers, body
