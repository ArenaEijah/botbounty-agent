from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def write_scan_report(
    ranked: list[dict],
    *,
    interesting: list[dict] | None = None,
    min_priority: float = 60,
    api_status: str = "ok",
    path: str = ".agent_reports/latest.md",
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# BotBounty Agent — Scan Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"API status: {api_status}",
        "",
        f"## Interesting opportunities (priority >= {min_priority})",
        "",
        "Feasibility is evaluated read-only from the available task text and requirements.",
        "",
        "| # | Title | Reward | Efficiency | Score | Priority | Eligibility | Feasibility | Requirements | Status |",
        "|---:|---|---:|---:|---:|---:|---|---|---|---|",
    ]

    selected = interesting if interesting is not None else ranked
    eligibility_counts = {"ELIGIBLE": 0, "REVIEW": 0, "NOT_ELIGIBLE": 0}
    readiness_counts = {"READY": 0, "REVIEW": 0, "NOT_RECOMMENDED": 0}
    for bounty in ranked:
        eligibility = bounty.get("_agent_eligibility", "REVIEW")
        readiness = bounty.get("_agent_solution_readiness", "REVIEW")
        eligibility_counts[eligibility] = eligibility_counts.get(eligibility, 0) + 1
        readiness_counts[readiness] = readiness_counts.get(readiness, 0) + 1

    lines[lines.index("") + 1:lines.index("", lines.index("") + 1)] = [
        f"Total bounties scanned: {len(ranked)}",
        f"Eligibility: {eligibility_counts['ELIGIBLE']} eligible, {eligibility_counts['REVIEW']} review, {eligibility_counts['NOT_ELIGIBLE']} not eligible",
        f"Solution readiness: {readiness_counts['READY']} ready, {readiness_counts['REVIEW']} review, {readiness_counts['NOT_RECOMMENDED']} not recommended",
    ]
    if not selected:
        lines.append("| No opportunities currently meet the priority threshold. | | | | | | | |")
    for index, bounty in enumerate(selected[:10], start=1):
        title = str(
            bounty.get("title")
            or bounty.get("name")
            or f"Bounty {bounty.get('id', '?')}"
        ).replace("|", "\\|")
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

        lines.append(
            f"| {index} | {title} | {reward} | "
            f"{bounty.get('_agent_efficiency', 0)} | "
            f"{bounty.get('_agent_score', 0)} | "
            f"{bounty.get('_agent_priority', bounty.get('_agent_score', 0))} | "
            f"{bounty.get('_agent_eligibility', 'REVIEW')} | "
            f"{bounty.get('_agent_feasibility', 'REVIEW')} | "
            f"{bounty.get('_agent_requirements_status', 'REVIEW')} | {status} |"
        )

        reasons = bounty.get("_agent_requirements_reasons") or []
        if reasons:
            lines.append(f"  - Requirements review: {'; '.join(str(reason) for reason in reasons)}")

        eligibility_reasons = bounty.get("_agent_eligibility_reasons") or []
        if eligibility_reasons:
            lines.append(f"  - Eligibility: {'; '.join(str(reason) for reason in eligibility_reasons)}")

        feasibility_reasons = bounty.get("_agent_feasibility_reasons") or []
        if feasibility_reasons:
            lines.append(f"  - Feasibility review: {'; '.join(str(reason) for reason in feasibility_reasons)}")

    lines.extend([
        "",
        "## Safety",
        "",
        "- Read-only scan.",
        "- No claim, submission, wallet action, or payment was performed.",
    ])

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
