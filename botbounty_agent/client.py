import httpx


class BotBountyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=20.0, follow_redirects=True)

    def close(self) -> None:
        self.client.close()

    def list_bounties(self):
        response = self.client.get(f"{self.base_url}/agent/bounties")
        if response.status_code >= 500:
            return {
                "bounties": [],
                "_agent_api_error": (
                    f"BotBounty API returned HTTP {response.status_code}. "
                    "The API is temporarily unavailable."
                ),
            }
        response.raise_for_status()
        return response.json()
