from __future__ import annotations

import re
from typing import Any


def _text(bounty: dict[str, Any]) -> str:
    parts = []
    for key in ("title", "description", "category", "tags", "requirements"):
        value = bounty.get(key)
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif isinstance(value, dict):
            parts.extend(str(item) for item in value.values())
        elif value is not None:
            parts.append(str(value))
    return " ".join(parts).lower()


def _reward(bounty: dict[str, Any]) -> float:
    for key in ("reward_usd", "bounty_usd", "amount_usd", "reward"):
        value = bounty.get(key)
        if isinstance(value, dict):
            value = value.get("usd") or value.get("amount") or value.get("value")
        try:
            return float(value)
        except (TypeError, ValueError):
            pass
        if isinstance(value, str):
            match = re.search(r"[-+]?\d+(?:[.,]\d+)?", value)
            if match:
                try:
                    return float(match.group(0).replace(",", "."))
                except ValueError:
                    pass
    return 0.0


def _effort_adjustment(text: str) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []
    low_effort = ("small", "simple", "quick", "minor", "fix", "typo")
    high_effort = (
        "complex", "large", "full-stack", "integration", "migrate",
        "migration", "deploy", "architecture",
    )
    if any(re.search(rf"\b{re.escape(word)}\b", text) for word in low_effort):
        score += 5
        reasons.append("likely lower effort")
    if any(re.search(rf"\b{re.escape(word)}\b", text) for word in high_effort):
        score -= 8
        reasons.append("likely higher effort")
    return score, reasons


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

    if reward >= 50:
        score += 15
        reasons.append("strong reward")
    elif reward >= 20:
        score += 8
        reasons.append("good reward")

    preferred = {"code": 18, "automation": 16, "data": 12, "research": 10}
    for keyword, points in preferred.items():
        if re.search(rf"\b{re.escape(keyword)}\b", text):
            score += points
            reasons.append(keyword)
            break

    if any(
        re.search(rf"\b{re.escape(word)}\b", text)
        for word in ("api", "python", "script", "bug", "debug", "etl")
    ):
        score += 8
        reasons.append("technical fit")

    effort_score, effort_reasons = _effort_adjustment(text)
    score += effort_score
    reasons.extend(effort_reasons)

    if any(
        re.search(rf"\b{re.escape(word)}\b", text)
        for word in ("urgent", "asap", "today", "deadline")
    ):
        score -= 3
        reasons.append("time pressure")

    return score, reasons


def estimated_efficiency(bounty: dict[str, Any]) -> tuple[float, str]:
    """Estimate reward efficiency from reward and detected effort."""
    reward = _reward(bounty)
    text = _text(bounty)
    high = ("complex", "large", "full-stack", "integration", "migrate", "migration", "deploy", "architecture")
    low = ("small", "simple", "quick", "minor", "fix", "typo")
    if any(word in text for word in high):
        return round(reward * 0.65, 2), "high effort"
    if any(word in text for word in low):
        return round(reward * 1.15, 2), "low effort"
    return round(reward, 2), "standard effort"

def feasibility_check(bounty: dict[str, Any]) -> tuple[str, list[str]]:
    """Classify whether the current agent appears able to handle the bounty."""
    text = _text(bounty)
    reasons: list[str] = []
    blocked = ("wallet", "private key", "seed phrase", "solidity", "smart contract", "on-chain")
    supported = ("python", "api", "script", "automation", "data", "research", "bug", "debug", "etl")
    high_effort = ("full-stack", "architecture", "large", "complex", "migration", "deploy")

    if any(word in text for word in blocked):
        return "NOT_RECOMMENDED", ["requires capability outside current safe agent scope"]
    if any(word in text for word in high_effort) and not any(word in text for word in supported):
        return "REVIEW", ["high-complexity task needs human review"]
    if any(word in text for word in supported):
        reasons.append("matches current technical capabilities")
        if any(word in text for word in high_effort):
            reasons.append("complexity requires review")
            return "REVIEW", reasons
        return "FEASIBLE", reasons
    return "REVIEW", ["insufficient task signals to confirm capability"]



def requirements_completeness(bounty: dict[str, Any]) -> tuple[str, list[str]]:
    """Assess whether a bounty has enough concrete information for a solution draft."""
    title = str(bounty.get("title") or bounty.get("name") or "").strip()
    description = str(bounty.get("description") or "").strip()
    requirements = bounty.get("requirements")
    combined = " ".join(_text(bounty).split())
    reasons: list[str] = []

    if not title:
        reasons.append("missing task title")
    if len(description) < 40:
        reasons.append("description is too short")
    if not requirements:
        reasons.append("explicit requirements are missing")

    concrete_signals = ("input", "output", "acceptance", "expected", "must", "return", "endpoint", "file", "test")
    if not any(signal in combined for signal in concrete_signals):
        reasons.append("no concrete acceptance or interface signal detected")

    if reasons:
        return "REVIEW", reasons
    return "READY", ["requirements contain concrete implementation signals"]

def clarity_adjustment(bounty: dict[str, Any]) -> tuple[float, list[str]]:
    """Adjust priority using concrete task signals without performing any external action."""
    title = str(bounty.get("title") or bounty.get("name") or "").strip()
    description = str(bounty.get("description") or "").strip()
    requirements = bounty.get("requirements")
    score = 0.0
    reasons: list[str] = []

    if title:
        score += 2
        reasons.append("clear title")
    if len(description) >= 120:
        score += 4
        reasons.append("detailed description")
    elif len(description) < 40:
        score -= 5
        reasons.append("vague description")

    if requirements:
        score += 4
        reasons.append("explicit requirements")
    else:
        score -= 4
        reasons.append("missing requirements")

    return score, reasons


def solution_readiness(bounty: dict[str, Any]) -> tuple[str, list[str]]:
    """Combine feasibility and requirement checks into one safe draft gate."""
    feasibility, feasibility_reasons = feasibility_check(bounty)
    completeness, completeness_reasons = requirements_completeness(bounty)
    reasons = list(feasibility_reasons) + list(completeness_reasons)

    if feasibility == "NOT_RECOMMENDED":
        return "NOT_RECOMMENDED", reasons
    if feasibility != "FEASIBLE" or completeness != "READY":
        return "REVIEW", reasons
    return "READY", reasons


def opportunity_priority(bounty: dict[str, Any]) -> tuple[float, list[str]]:
    """Add safe, read-only signals to the base score."""
    priority = float(bounty.get("_agent_score", 0))
    reasons: list[str] = []

    if not bounty.get("_agent_seen_before"):
        priority += 10
        reasons.append("new opportunity")
    elif bounty.get("_agent_changed"):
        priority += 12
        reasons.append("changed opportunity")

    reward = _reward(bounty)
    clarity_score, clarity_reasons = clarity_adjustment(bounty)
    priority += clarity_score
    reasons.extend(clarity_reasons)
    efficiency, effort_label = estimated_efficiency(bounty)
    bounty["_agent_efficiency"] = efficiency
    bounty["_agent_effort"] = effort_label
    if efficiency >= 50:
        priority += 5
        reasons.append("strong reward/effort ratio")
    elif efficiency < 10 and reward > 0:
        priority -= 3
        reasons.append("weak reward/effort ratio")

    if reward >= 50:
        priority += 5
        reasons.append("high-value opportunity")

    return round(priority, 1), reasons


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
