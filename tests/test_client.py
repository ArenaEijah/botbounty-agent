import unittest
from unittest.mock import Mock, patch

from botbounty_agent.client import BotBountyClient


class ClientTests(unittest.TestCase):
    def test_empty_bounty_id_is_rejected(self):
        client = BotBountyClient("https://example.test/api")
        try:
            with self.assertRaises(ValueError):
                client.get_bounty(" ")
        finally:
            client.close()

    @patch("botbounty_agent.client.httpx.Client")
    def test_invalid_json_returns_safe_error(self, client_cls):
        response = Mock(status_code=200)
        response.raise_for_status.return_value = None
        response.json.side_effect = ValueError("bad json")
        client_http = client_cls.return_value
        client_http.get.return_value = response
        client = BotBountyClient("https://example.test/api")
        try:
            result = client.list_bounties()
            self.assertIn("_agent_api_error", result)
            self.assertEqual(result["bounties"], [])
        finally:
            client.close()

    @patch("botbounty_agent.client.httpx.Client")
    def test_transient_http_error_is_retried(self, client_cls):
        response = Mock(status_code=503)
        client_http = client_cls.return_value
        client_http.get.return_value = response
        client = BotBountyClient("https://example.test/api")
        try:
            with patch("botbounty_agent.client.time.sleep"):
                result = client.list_bounties()
            self.assertIn("_agent_api_error", result)
            self.assertEqual(client_http.get.call_count, 3)
        finally:
            client.close()


if __name__ == "__main__":
    unittest.main()
