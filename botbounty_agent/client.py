import time

import httpx


class BotBountyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=20.0, follow_redirects=True)

    def close(self) -> None:
        self.client.close()

    def list_bounties(self):
        url = f"{self.base_url}/agent/bounties"
        retryable_statuses = {500, 502, 503, 504}

        for attempt in range(1, 4):
            response = self.client.get(url)

            if response.status_code not in retryable_statuses:
                response.raise_for_status()
                return response.json()

            if attempt < 3:
                time.sleep(attempt)

        return {
            "bounties": [],
            "_agent_api_error": (
                f"BotBounty API returned HTTP {response.status_code} "
                f"after 3 attempts. The API is temporarily unavailable."
            ),
        }
