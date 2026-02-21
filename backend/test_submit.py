import requests
import base64
dummy_tx = base64.b64encode(b'dummy_msgpack_transaction_data').decode('utf-8')
res = requests.post("http://localhost:8000/submit", json={"signed_txn": dummy_tx})
print("Upload Result:", res.json())
