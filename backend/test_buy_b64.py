import requests
res = requests.post("http://localhost:8000/investments/buy", json={"property_id": 1, "investor_address": "26ZTTSPZLZ3D6HQQ7YF247AOBP44HOKUKR2PQQ7H5W3RJQ3OQBURZZMNJQ", "quantity": 10})
print("Result:", res.json())
payload = res.json()["unsigned_txns"][0]
print("Base64 Length:", len(payload))
print("Payload:", payload)
