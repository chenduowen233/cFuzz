import json
import random
import string


# 加载 HTTP/2 规则集
def load_http2_rules(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


# 随机生成一个字符串（用于绕过缓存）
def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# 根据规则集生成随机 HTTP/2 请求头
def generate_headers(rules):
    headers = {}
    # 必要 HTTP/2 标头
    headers[":method"] = random.choice(rules["http_methods"])
    # 在路径末尾添加 ?{random}
    base_path = random.choice(rules["paths"]).replace("{random_id}", str(random.randint(1000, 9999)))
    headers[":path"] = f"{base_path}?{generate_random_string(12)}"
    headers[":scheme"] = random.choice(rules["schemes"])
    #headers[":authority"] = f"example{random.randint(1, 10)}.com"
    #headers[":authority"] = "tbg.iinfinity.cn"

    # 常用头部
    headers["user-agent"] = random.choice(rules["user_agents"])
    headers["accept"] = random.choice(rules["accept_values"])
    headers["accept-language"] = random.choice(rules["languages"])
    headers["content-type"] = random.choice(rules["content_types"])
    headers["cache-control"] = random.choice(rules["cache_controls"])

    # 可选标头
    if random.choice([True, False]):
        headers["forwarded"] = random.choice(rules["forwarded_values"])
    if random.choice([True, False]):
        headers["cookie"] = random.choice(rules["cookie_values"])
    if random.choice([True, False]):
        headers["authorization"] = f"{random.choice(rules['authorization_schemes'])} token-{random.randint(10000, 99999)}"
    if random.choice([True, False]):
        headers["etag"] = random.choice(rules["etag_values"])
    if random.choice([True, False]):
        headers["if-match"] = random.choice(rules["if_match_values"])
    if random.choice([True, False]):
        headers["if-none-match"] = random.choice(rules["if_none_match_values"])
    if random.choice([True, False]):
        headers["if-modified-since"] = random.choice(rules["if_modified_since_values"])
    if random.choice([True, False]):
        headers["if-unmodified-since"] = random.choice(rules["if_unmodified_since_values"])
    if random.choice([True, False]):
        headers["if-range"] = random.choice(rules["if_range_values"])
    if random.choice([True, False]):
        headers["range"] = random.choice(rules["range_values"])

    # 自定义头部
    for _ in range(random.randint(1, 5)):
        custom_header = random.choice(rules["custom_headers"])
        headers[custom_header] = random.choice(rules["parameter_values"])

    return headers


# 根据 content-type 生成随机请求体
def generate_body(content_type, rules):
    if content_type == "application/json":
        return json.dumps({
            random.choice(rules["parameter_names"]): random.choice(rules["parameter_values"])
            for _ in range(random.randint(1, 5))
        })
    elif content_type == "application/x-www-form-urlencoded":
        return "&".join([
            f"{random.choice(rules['parameter_names'])}={random.choice(rules['parameter_values'])}"
            for _ in range(random.randint(1, 5))
        ])
    elif content_type == "text/plain":
        return " ".join(random.choices(rules["parameter_values"], k=random.randint(3, 10)))
    return ""


# 生成完整 HTTP/2 请求
def generate_request(file_path="../rule/important_rules.json"):
    rules = load_http2_rules(file_path)
    headers = generate_headers(rules)
    body = generate_body(headers["content-type"], rules)
    return headers, body


# 测试生成请求
if __name__ == "__main__":
    headers, body = generate_request()
    print("Generated Headers:")
    print(json.dumps(headers, indent=4))
    print("\nGenerated Body:")
    print(body)
