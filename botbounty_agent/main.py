from .client import BotBountyClient
from .config import Config
from .scoring import rank_bounties


def _items(payload):
    if isinstance(payload, dict):
        for key in ("bounties", "data", "items", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        return [payload]
    return payload if isinstance(payload, list) else []


def main() -> None:
    config = Config()
    print("BotBounty Agent — simulation:", config.dry_run)
    print("Minimum bounty:", config.min_bounty_usd, "USD")

    client = BotBountyClient(config.api_base)
    try:
        payload = client.list_bounties()
        bounties = _items(payload)
        ranked = rank_bounties(bounties, config.min_bounty_usd)

        print(f"Bounties returned: {len(bounties)}")
        print("Top candidates:")
        for index, bounty in enumerate(ranked[:5], start=1):
            title = bounty.get("title") or bounty.get("name") or f"Bounty {bounty.get('id', '?')}"
            reward = bounty.get("reward_usd", bounty.get("bounty_usd", bounty.get("amount_usd", bounty.get("reward", "?"))))
            print(f"{index}. {title} | reward={reward} | score={bounty['_agent_score']}")
            if bounty["_agent_reasons"]:
                print("   reasons:", ", ".join(bounty["_agent_reasons"]))

        print("Read-only scan complete. No claim, submission, wallet action, or payment was performed.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
