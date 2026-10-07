from pathlib import Path

from .client import BotBountyClient
from .config import Config
from .scoring import feasibility_check, opportunity_priority, rank_bounties
from .history import BountyHistory
from .report import write_scan_report
def _prepare_work(bounty):
    text = ' '.join(str(bounty.get(key, '')) for key in ('title', 'description', 'requirements', 'category', 'tags')).lower()
    deliverables = []
    if any(word in text for word in ('python', 'script', 'automation')):
        deliverables.append('Python script or automation implementation')
    if 'api' in text:
        deliverables.append('API integration or tested API calls')
    if any(word in text for word in ('bug', 'fix', 'debug')):
        deliverables.append('bug fix with verification/tests')
    if any(word in text for word in ('data', 'etl')):
        deliverables.append('data processing/output')
    if not deliverables:
        deliverables.append('implementation matching the stated requirements')
    missing = []
    if not bounty.get('description'):
        missing.append('full description')
    if not bounty.get('requirements'):
        missing.append('explicit requirements')
    return deliverables, missing



def _execution_plan(bounty):
    text = ' '.join(str(bounty.get(key, '')) for key in ('title', 'description', 'requirements', 'category', 'tags')).lower()
    steps = [
        "1. Re-read the complete bounty description and requirements.",
        "2. Confirm inputs, acceptance criteria, constraints, and required output format.",
    ]
    if "api" in text:
        steps.append("3. Inspect the API contract, endpoints, authentication needs, and expected responses.")
    elif any(word in text for word in ("python", "script", "automation")):
        steps.append("3. Design the smallest Python/automation implementation that satisfies the requirements.")
    else:
        steps.append("3. Break the requested work into the smallest verifiable implementation steps.")
    if any(word in text for word in ("bug", "fix", "debug")):
        steps.append("4. Reproduce or isolate the issue, apply the minimal fix, and add a regression check.")
    else:
        steps.append("4. Implement the solution incrementally and verify each requirement.")
    steps.extend([
        "5. Run relevant tests/checks and verify the acceptance criteria.",
        "6. Review the final deliverables against every stated requirement.",
        "7. Prepare the result for review; do not submit or claim the bounty automatically.",
    ])
    return steps

def _save_draft(bounty_id, draft):
    target = Path('.agent_drafts') / f'{bounty_id or "unknown"}.md'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(draft + '\n', encoding='utf-8')
    return target

def _draft_deliverable(bounty):
    title = bounty.get("title") or bounty.get("name") or "Selected bounty"
    text = " ".join(str(bounty.get(key, "")) for key in ("title", "description", "requirements", "category", "tags")).lower()
    lines = [
        "# Draft Deliverable",
        "",
        f"## Task",
        str(title),
        "",
        "## Proposed solution",
    ]
    if "api" in text:
        lines.extend([
            "1. Define the required API inputs and expected responses.",
            "2. Implement the smallest client/request flow needed by the requirements.",
            "3. Add error handling and response validation.",
        ])
    elif any(word in text for word in ("python", "script", "automation")):
        lines.extend([
            "1. Create a focused Python implementation matching the stated inputs and outputs.",
            "2. Keep configuration and secrets outside source code.",
            "3. Add validation and automated tests for the main path and failure cases.",
        ])
    elif any(word in text for word in ("bug", "fix", "debug")):
        lines.extend([
            "1. Reproduce the reported behavior.",
            "2. Isolate the smallest responsible change.",
            "3. Add a regression test and verify the fix.",
        ])
    else:
        lines.extend([
            "1. Translate the stated requirements into concrete implementation tasks.",
            "2. Implement the smallest verifiable solution.",
            "3. Validate the output against the acceptance criteria.",
        ])
    lines.extend([
        "",
        "## Validation checklist",
        "- Requirements reviewed",
        "- Acceptance criteria checked",
        "- Tests/checks completed",
        "- Secrets and credentials excluded",
        "",
        "## Safety",
        "This is a draft only. It has not been submitted, claimed, deployed, or used for any payment or wallet action.",
    ])
    return "\n".join(lines)

def _generate_solution_files(bounty_id, bounty):
    root = Path(".agent_drafts") / f"{bounty_id or 'unknown'}-solution"
    root.mkdir(parents=True, exist_ok=True)
    title = bounty.get("title") or bounty.get("name") or "Selected bounty"
    description = " ".join(str(bounty.get("description", "")).split())
    readme = [
        "# Solution Draft",
        "",
        f"Task: {title}",
        "",
        "## Scope",
        description[:2000] if description else "Detailed description was not available.",
        "",
        "## Status",
        "Draft only. Review requirements and acceptance criteria before use.",
        "",
        "## Safety",
        "No claim, submission, deployment, wallet action, payment, or credential storage is performed by this draft.",
    ]
    (root / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")

    requirements = bounty.get("requirements") or "No explicit requirements were provided."
    if isinstance(requirements, dict):
        requirement_lines = [f"{key}: {value}" for key, value in requirements.items()]
    elif isinstance(requirements, list):
        requirement_lines = [str(item).strip() for item in requirements if str(item).strip()]
    else:
        requirement_lines = [line.strip(" -*\\t") for line in str(requirements).splitlines() if line.strip()]
    if not requirement_lines:
        requirement_lines = [str(requirements).strip()]
    spec = [
        "# Solution Specification",
        "",
        f"## Task\\n{title}",
        "",
        "## Requirements",
    ]
    spec.extend(f"- {line}" for line in requirement_lines[:30])
    spec.extend([
        "",
        "## Acceptance checklist",
        *[f"- [ ] Verify: {line}" for line in requirement_lines[:30]],
        "- [ ] Add tests for the main success path",
        "- [ ] Add tests for relevant failure/edge cases",
        "- [ ] Confirm no secrets or private credentials are embedded",
        "- [ ] Human review completed before any submission",
    ])
    (root / "SOLUTION_SPEC.md").write_text("\n".join(spec) + "\n", encoding="utf-8")

    text = " ".join(str(bounty.get(key, "")) for key in ("title", "description", "requirements", "category", "tags")).lower()
    if any(word in text for word in ("python", "script", "automation", "api", "data", "etl", "bug", "fix", "debug")):
        if "api" in text:
            implementation = '''"""Initial API solution draft. Unverified against the bounty acceptance criteria."""
import os
from typing import Any
import httpx


def get_json(url: str, *, timeout: float = 20.0) -> Any:
    """Fetch JSON without embedding credentials in source code."""
    headers = {}
    token = os.getenv("API_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = httpx.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()


def main() -> None:
    raise NotImplementedError("Map the verified bounty inputs and endpoint to get_json().")


if __name__ == "__main__":
    main()
'''
        elif any(word in text for word in ("data", "etl")):
            implementation = '''"""Initial data-processing solution draft. Unverified."""
from collections.abc import Iterable


def transform(rows: Iterable[dict]) -> list[dict]:
    """Return normalized row copies; customize fields after requirements review."""
    return [dict(row) for row in rows]


def main() -> None:
    raise NotImplementedError("Map the verified input/output format to transform().")


if __name__ == "__main__":
    main()
'''
        elif any(word in text for word in ("bug", "fix", "debug")):
            implementation = '''"""Initial bug-fix solution draft. Unverified."""
def reproduce_or_validate() -> None:
    """Replace with the smallest regression check derived from the report."""
    raise NotImplementedError("Implement after reproducing the reported behavior.")


if __name__ == "__main__":
    reproduce_or_validate()
'''
        else:
            implementation = '''"""Initial Python/automation solution draft. Unverified."""
from typing import Any


def run(input_data: Any) -> Any:
    """Small deterministic entry point to adapt to the verified requirements."""
    return input_data


def main() -> None:
    raise NotImplementedError("Map the verified inputs, outputs, and acceptance criteria to run().")


if __name__ == "__main__":
    main()
'''
        (root / "solution.py").write_text(implementation, encoding="utf-8")
        if "api" in text:
            tests = '''"""Initial API draft tests."""
from solution import get_json


def test_get_json_is_available():
    assert callable(get_json)
'''
        elif any(word in text for word in ("data", "etl")):
            tests = '''"""Initial data draft tests."""
from solution import transform


def test_transform_copies_rows():
    source = [{"value": 1}]
    assert transform(source) == source
    assert transform(source) is not source
'''
        elif any(word in text for word in ("bug", "fix", "debug")):
            tests = '''"""Initial regression-test placeholder."""
from solution import reproduce_or_validate


def test_regression_hook_exists():
    assert callable(reproduce_or_validate)
'''
        else:
            tests = '''"""Initial Python/automation draft tests."""
from solution import run


def test_run_preserves_input_until_requirements_are_mapped():
    assert run({"sample": 1}) == {"sample": 1}
'''
        (root / "test_solution.py").write_text(tests, encoding="utf-8")
    return root

def _validate_solution_draft(root):
    """Run lightweight static validation without executing generated solution code."""
    checks = []
    solution = root / "solution.py"
    tests = root / "test_solution.py"
    if solution.exists():
        compile(solution.read_text(encoding="utf-8"), str(solution), "exec")
        checks.append("solution syntax: OK")
    if tests.exists():
        compile(tests.read_text(encoding="utf-8"), str(tests), "exec")
        checks.append("test syntax: OK")
    forbidden = ("private key", "seed phrase", "mnemonic", "wallet secret")
    combined = ""
    for path in (solution, tests, root / "README.md", root / "SOLUTION_SPEC.md"):
        if path.exists():
            combined += path.read_text(encoding="utf-8").lower()
    if any(term in combined for term in forbidden):
        checks.append("security scan: REVIEW")
    else:
        checks.append("security scan: OK")
    return checks


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

        interesting = [item for item in ranked if item.get("_agent_priority", 0) >= config.min_priority]
        for bounty in ranked[:3]:
            feasibility, feasibility_reasons = feasibility_check(bounty)
            bounty["_agent_feasibility"] = feasibility
            bounty["_agent_feasibility_reasons"] = feasibility_reasons
        print(f"Bounties returned: {len(bounties)}")
        print(f"Interesting opportunities (priority >= {config.min_priority}): {len(interesting)}")
        write_scan_report(ranked, interesting=interesting, min_priority=config.min_priority)

        print(f"New bounty IDs: {new_count}")
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
            print(f"{index}. {title} | reward={reward} | score={bounty['_agent_score']} | priority={bounty.get('_agent_priority', bounty['_agent_score'])} | feasibility={bounty.get('_agent_feasibility', 'REVIEW')} | {status}")
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

            # Re-check feasibility using the richer detail, still read-only.
            enriched = dict(bounty)
            if description is not None:
                enriched["description"] = description
            if requirements is not None:
                enriched["requirements"] = requirements
            if bounty.get("_agent_feasibility") != "NOT_RECOMMENDED":
                feasibility, feasibility_reasons = feasibility_check(enriched)
                bounty["_agent_feasibility"] = feasibility
                bounty["_agent_feasibility_reasons"] = feasibility_reasons

            print(f"   details loaded: {bounty_id}")
            if description:
                compact = " ".join(str(description).split())
                print("   description:", compact[:300])
            if requirements:
                print("   requirements:", requirements)
            print("   feasibility:", bounty.get("_agent_feasibility", "REVIEW"))
            print("   feasibility reasons:", ", ".join(bounty.get("_agent_feasibility_reasons", [])))
            if bounty.get("_agent_feasibility") == "FEASIBLE":
                deliverables, missing = _prepare_work(enriched)
                bounty["_agent_deliverables"] = deliverables
                bounty["_agent_missing"] = missing
                bounty["_agent_execution_plan"] = _execution_plan(enriched)
                bounty["_agent_draft"] = _draft_deliverable(enriched)
                draft_path = _save_draft(bounty_id, bounty["_agent_draft"])
                solution_path = _generate_solution_files(bounty_id, enriched)
                print("   solution draft files:", solution_path)
                validation = _validate_solution_draft(solution_path)
                print("   draft validation:", "; ".join(validation))
                print("   proposed deliverables:", "; ".join(deliverables))
                print("   draft deliverable prepared:", draft_path)
                print("   draft deliverable prepared:", "yes")
                print("   execution plan:")
                for step in bounty["_agent_execution_plan"]:
                    print("     ", step)
                if missing:
                    print("   missing information:", "; ".join(missing))

        print(f"Read-only detail enrichment: {detailed_count} candidate(s).")
        print("Read-only scan complete. No claim, submission, wallet action, or payment was performed.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
