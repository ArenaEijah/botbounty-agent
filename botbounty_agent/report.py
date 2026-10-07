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
        "| # | Title | Reward | Efficiency | Score | Priority | Feasibility | Status |",
        "|---:|---|---:|---:|---:|---:|---|---|",
    ]

    selected = interesting if interesting is not None else ranked
    if not selected:
        lines.append("| No opportunities currently meet the priority threshold. | | | | | |")
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
            f"{bounty.get('_agent_feasibility', 'REVIEW')} | {status} |"
        )

    lines.extend([
        "",
        "## Safety",
        "",
        "- Read-only scan.",
        "- No claim, submission, wallet action, or payment was performed.",
    ])

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
