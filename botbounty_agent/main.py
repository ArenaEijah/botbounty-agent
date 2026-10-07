from .client import BotBountyClient
from .config import Config
from .scoring import opportunity_priority, rank_bounties
from .history import BountyHistory
from .report import write_scan_report


def _items(payload):
    if isinstance(payload, dict):
        for key in ("bounties", "data", "items", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        return [payload]
    return payload if isinstance(payload, list) else []


def _bounty_id(bounty):
    for key in ("id", "bounty_id"):
        value = bounty.get(key)
        if value is not None and str(value).strip():
            return value
    return None


def _detail_summary(detail):
    if not isinstance(detail, dict):
        return None

    for key in ("bounty", "data", "result"):
        value = detail.get(key)
        if isinstance(value, dict):
            return value

    return detail


def main() -> None:
    config = Config()
    print("BotBounty Agent — simulation:", config.dry_run)
    print("Minimum bounty:", config.min_bounty_usd, "USD")

    history = BountyHistory()
    client = BotBountyClient(config.api_base)
    try:
        payload = client.list_bounties()

        if isinstance(payload, dict) and payload.get("_agent_api_error"):
            print("API status:", payload["_agent_api_error"])
            write_scan_report([], api_status=payload["_agent_api_error"])
            print("Scan paused safely. No claim, submission, wallet action, or payment was performed.")
            return

        bounties = _items(payload)
        ranked = rank_bounties(bounties, config.min_bounty_usd)

        new_count = 0
        for bounty in ranked:
            bounty_id = _bounty_id(bounty)
            bounty["_agent_seen_before"] = history.contains(bounty_id)
            bounty["_agent_changed"] = history.changed(bounty_id, bounty)
            if bounty_id is not None and (not bounty["_agent_seen_before"] or bounty["_agent_changed"]):
                new_count += 1
            history.mark_seen(bounty_id, bounty)
            priority, priority_reasons = opportunity_priority(bounty)
            bounty["_agent_priority"] = priority
            bounty["_agent_priority_reasons"] = priority_reasons
        history.save()
        ranked.sort(key=lambda item: (item.get("_agent_priority", item.get("_agent_score", 0)), item.get("_agent_score", 0)), reverse=True)

        print(f"Bounties returned: {len(bounties)}")
        write_scan_report(ranked)

        print(f"New bounty IDs: {new_count}")
        print(f"Interesting opportunities (priority >= {config.min_priority}): {len(interesting)}")
        print("Top candidates:")

        for index, bounty in enumerate(ranked[:5], start=1):
            title = bounty.get("title") or bounty.get("name") or f"Bounty {bounty.get('id', '?')}"
            reward = bounty.get(
                "reward_usd",
                bounty.get("bounty_usd", bounty.get("amount_usd", bounty.get("reward", "?"))),
            )
            if not bounty.get("_agent_seen_before"):
                status = "NEW"
            elif bounty.get("_agent_changed"):
                status = "CHANGED"
            else:
                status = "seen"
            print(f"{index}. {title} | reward={reward} | score={bounty['_agent_score']} | priority={bounty.get('_agent_priority', bounty['_agent_score'])} | {status}")
            if bounty["_agent_reasons"]:
                print("   reasons:", ", ".join(bounty["_agent_reasons"]))

        # Read-only enrichment: inspect details for the top 3 candidates.
        # No claim, submit, wallet, or payment endpoint is called.
        detailed_count = 0
        for bounty in ranked[:3]:
            bounty_id = _bounty_id(bounty)
            if bounty_id is None:
                continue

            try:
                detail = _detail_summary(client.get_bounty(bounty_id))
            except Exception as exc:
                print(f"   detail unavailable for {bounty_id}: {exc}")
                continue

            if isinstance(detail, dict) and detail.get("_agent_api_error"):
                print(f"   detail unavailable for {bounty_id}: {detail['_agent_api_error']}")
                continue

            detailed_count += 1
            description = detail.get("description")
            requirements = detail.get("requirements")

            print(f"   details loaded: {bounty_id}")
            if description:
                compact = " ".join(str(description).split())
                print("   description:", compact[:300])
            if requirements:
                print("   requirements:", requirements)

        print(f"Read-only detail enrichment: {detailed_count} candidate(s).")
        print("Read-only scan complete. No claim, submission, wallet action, or payment was performed.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
