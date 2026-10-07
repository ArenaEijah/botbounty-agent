from .client import BotBountyClient
from .config import Config

def main() -> None:
    config = Config()
    print("BotBounty Agent — simulation:", config.dry_run)
    print("Minimum bounty:", config.min_bounty_usd, "USD")

    client = BotBountyClient(config.api_base)
    try:
        bounties = client.list_bounties()
        if isinstance(bounties, dict):
            items = bounties.get("bounties", bounties.get("data", bounties))
        else:
            items = bounties
        if not isinstance(items, list):
            items = [items]
        print(f"Bounties returned: {len(items)}")
        for bounty in items[:10]:
            print(bounty)
        print("Read-only scan complete. No claim or submission was performed.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
