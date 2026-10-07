from __future__ import annotations

from typing import Any


def _text(bounty: dict[str, Any]) -> str:
    parts = []
    for key in ("title", "description", "category", "tags", "requirements"):
        value = bounty.get(key)
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif value is not None:
            parts.append(str(value))
    return " ".join(parts).lower()


def _reward(bounty: dict[str, Any]) -> float:
    for key in ("reward_usd", "bounty_usd", "amount_usd", "reward"):
        value = bounty.get(key)
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return 0.0


def score_bounty(bounty: dict[str, Any], minimum_usd: float) -> tuple[float, list[str]]:
    text = _text(bounty)
    reward = _reward(bounty)
    score = 0.0
    reasons: list[str] = []

    if reward >= minimum_usd:
        score += 40
        reasons.append("reward meets minimum")
    elif reward > 0:
        score += 10

    preferred = {
        "code": 18,
        "automation": 16,
        "data": 12,
        "research": 10,
    }
    for keyword, points in preferred.items():
        if keyword in text:
            score += points
            reasons.append(keyword)
            break

    if any(word in text for word in ("api", "python", "script", "bug", "debug", "etl")):
        score += 8
        reasons.append("technical fit")

    if any(word in text for word in ("urgent", "asap", "today", "deadline")):
        score -= 3
        reasons.append("time pressure")

    return score, reasons


def rank_bounties(bounties: list[dict[str, Any]], minimum_usd: float) -> list[dict[str, Any]]:
    ranked = []
    for bounty in bounties:
        if not isinstance(bounty, dict):
            continue
        score, reasons = score_bounty(bounty, minimum_usd)
        item = dict(bounty)
        item["_agent_score"] = round(score, 1)
        item["_agent_reasons"] = reasons
        ranked.append(item)

    return sorted(
        ranked,
        key=lambda item: (item.get("_agent_score", 0), _reward(item)),
        reverse=True,
    )
