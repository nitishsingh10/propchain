from algosdk.v2client import algod
from algosdk import transaction, encoding
from algosdk.logic import get_application_address
import base64

client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
sp = client.suggested_params()
investor = "26ZTTSPZLZ3D6HQQ7YF247AOBP44HOKUKR2PQQ7H5W3RJQ3OQBURZZMNJQ"
receiver = investor
try:
    txn = transaction.PaymentTxn(
        sender=investor,
        sp=sp,
        receiver=receiver,
        amt=5075,
        note=f"PropChain: Buy 1 shares of Prop 1".encode()
    )
    encoded = base64.b64encode(encoding.msgpack_encode(txn)).decode("utf-8")
    print("Success:", encoded)
except Exception as e:
    import traceback
    traceback.print_exc()
