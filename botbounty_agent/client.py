import time
from urllib.parse import quote

import httpx


class BotBountyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=20.0, follow_redirects=True)

    def close(self) -> None:
        self.client.close()

    def _get_json_with_retry(self, path: str):
        url = f"{self.base_url}{path}"
        retryable_statuses = {500, 502, 503, 504}
        last_error = None

        for attempt in range(1, 4):
            try:
                response = self.client.get(url)
                if response.status_code not in retryable_statuses:
                    response.raise_for_status()
                    try:
                        return response.json()
                    except ValueError:
                        return {
                            "_agent_api_error": (
                                f"BotBounty API returned invalid JSON for {path} "
                                f"(HTTP {response.status_code})."
                            )
                        }
                last_error = (
                    f"BotBounty API returned HTTP {response.status_code} "
                    f"after attempt {attempt}."
                )
            except httpx.HTTPError as exc:
                last_error = f"BotBounty API request failed on attempt {attempt}: {exc}"

            if attempt < 3:
                time.sleep(attempt)

        return {
            "_agent_api_error": (
                f"{last_error or 'BotBounty API request failed.'} "
                "Scan paused safely after 3 attempts."
            )
        }

    def list_bounties(self):
        payload = self._get_json_with_retry("/agent/bounties")

        if isinstance(payload, dict) and payload.get("_agent_api_error"):
            payload["bounties"] = []
        return payload

    def get_bounty(self, bounty_id):
        if bounty_id is None or str(bounty_id).strip() == "":
            raise ValueError("bounty_id is required")

        safe_id = quote(str(bounty_id).strip(), safe="")
        return self._get_json_with_retry(f"/agent/bounties/{safe_id}")
