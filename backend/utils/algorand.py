"""PropChain — Algorand SDK Wrapper"""

import os
from algosdk.v2client import algod, indexer
from algosdk.transaction import wait_for_confirmation as _wait
from algosdk import encoding
from dotenv import load_dotenv

load_dotenv()


class AlgorandClient:
    """Wrapper around algosdk for common PropChain operations."""

    def __init__(self):
        self.algod = algod.AlgodClient(
            os.getenv("ALGOD_TOKEN", ""),
            os.getenv("ALGOD_SERVER", "https://testnet-api.algonode.cloud"),
        )
        self.indexer = indexer.IndexerClient(
            "", os.getenv("INDEXER_SERVER", "https://testnet-idx.algonode.cloud"),
        )

    def get_account_info(self, address: str) -> dict:
        return self.algod.account_info(address)

    def get_app_state(self, app_id: int) -> dict:
        info = self.algod.application_info(app_id)
        state = {}
        for kv in info.get("params", {}).get("global-state", []):
            key = encoding.base64.b64decode(kv["key"]).decode("utf-8", errors="ignore")
            val = kv["value"]
            state[key] = val.get("uint", val.get("bytes", ""))
        return state

    def wait_for_confirmation(self, txid: str, rounds: int = 4) -> dict:
        return _wait(self.algod, txid, rounds)

    def get_transaction(self, txid: str) -> dict:
        return self.indexer.transaction(txid)

    def get_suggested_params(self):
        return self.algod.suggested_params()

    def search_applications(self, app_id: int, **kwargs) -> dict:
        return self.indexer.search_transactions(application_id=app_id, **kwargs)
