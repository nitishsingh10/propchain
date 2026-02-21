import requests
res = requests.post("http://localhost:8000/investments/buy", json={"property_id": 3, "investor_address": "26ZTTSPZLZ3D6HQQ7YF247AOBP44HOKUKR2PQQ7H5W3RJQ3OQBURZZMNJQ", "quantity": 50})
txn_str = res.json()["unsigned_txns"][0]
print("Length:", len(txn_str))
data_chars = len(txn_str.replace("=", ""))
print("Data chars:", data_chars)
