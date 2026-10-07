import httpx

class BotBountyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=20.0, follow_redirects=True)

    def close(self) -> None:
        self.client.close()

    def list_bounties(self):
        response = self.client.get(f"{self.base_url}/agent/bounties")
        response.raise_for_status()
        return response.json()
