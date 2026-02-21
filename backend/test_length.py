from algosdk import transaction, encoding
sp = transaction.SuggestedParams(fee=1000, first=0, last=1000, gh="base64string"*4, flat_fee=True)
txn = transaction.PaymentTxn(
    sender="26ZTTSPZLZ3D6HQQ7YF247AOBP44HOKUKR2PQQ7H5W3RJQ3OQBURZZMNJQ",
    sp=sp,
    receiver="26ZTTSPZLZ3D6HQQ7YF247AOBP44HOKUKR2PQQ7H5W3RJQ3OQBURZZMNJQ",
    amt=50750,
    note=f"PropChain: Buy 50 shares of Prop 3".encode()
)
encoded = encoding.msgpack_encode(txn)
print("Length:", len(encoded))
