"""PropChain — IPFS Client (Pinata wrapper)"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()


class IPFSClient:
    """Async IPFS client wrapping Pinata API."""

    BASE_URL = "https://api.pinata.cloud"
    GATEWAY = "https://gateway.pinata.cloud/ipfs"

    def __init__(self):
        self.api_key = os.getenv("PINATA_API_KEY", "")
        self.api_secret = os.getenv("PINATA_SECRET", "")
        self.headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.api_secret,
        }

    async def upload_json(self, data: dict, name: str = "propchain") -> str:
        """Upload JSON to IPFS. Returns CID."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/pinning/pinJSONToIPFS",
                json={"pinataContent": data, "pinataMetadata": {"name": name}},
                headers=self.headers, timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()["IpfsHash"]
            raise Exception(f"Pinata error: {resp.status_code} {resp.text}")

    async def upload_file(self, file_path: str) -> str:
        """Upload file to IPFS. Returns CID."""
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                resp = await client.post(
                    f"{self.BASE_URL}/pinning/pinFileToIPFS",
                    files={"file": f}, headers=self.headers, timeout=60,
                )
            if resp.status_code == 200:
                return resp.json()["IpfsHash"]
            raise Exception(f"Pinata error: {resp.status_code} {resp.text}")

    def get_url(self, cid: str) -> str:
        """Get gateway URL for a CID."""
        return f"{self.GATEWAY}/{cid}"
