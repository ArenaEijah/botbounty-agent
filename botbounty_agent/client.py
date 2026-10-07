import httpx

class BotBountyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=20.0, follow_redirects=True)

    def close(self):
        self.client.close()
