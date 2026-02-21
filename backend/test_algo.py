from algosdk.v2client import algod
import os
algod_server = os.getenv("ALGOD_SERVER", "https://testnet-api.algonode.cloud")
algod_token = os.getenv("ALGOD_TOKEN", "")
client = algod.AlgodClient(algod_token, algod_server)
try:
    sp = client.suggested_params()
    print("Success: sp=", sp.fee)
except Exception as e:
    print("Exception:", str(e))
