from .config import Config

def main():
    config = Config()
    print("BotBounty Agent — simulation:", config.dry_run)
    print("Minimum bounty:", config.min_bounty_usd, "USD")
    print("No automatic submission or payment is enabled.")

if __name__ == "__main__":
    main()
