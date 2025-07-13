import requests

API_URL = "http://localhost:5000"

def test(payload: dict) -> requests.Response:
    """
    向 /users 端点发起 POST 请求，返回 Response 对象
    """
    url = f"{API_URL}/analyze"
    headers = {"Content-Type": "application/json"}
    return requests.post(url, json=payload, headers=headers)

payload = {"ticker":"600310"}

print(requests.get(f"{API_URL}/qwe",headers={"Content-Type": "application/json"}))