from __future__ import annotations

import hashlib
import json
from pathlib import Path


class BountyHistory:
    def __init__(self, path: str = ".agent_state/history.json"):
        self.path = Path(path)
        self.records: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, ValueError):
            return

        if isinstance(data, dict):
            self.records = {str(k): str(v) for k, v in data.items()}
        elif isinstance(data, list):
            # Backward compatibility with the previous ID-only format.
            self.records = {str(item): "" for item in data if str(item).strip()}

    def contains(self, bounty_id) -> bool:
        return bounty_id is not None and str(bounty_id) in self.records

    def fingerprint(self, bounty: dict) -> str:
        relevant = {
            key: bounty.get(key)
            for key in (
                "title",
                "description",
                "reward_usd",
                "bounty_usd",
                "amount_usd",
                "reward",
                "status",
                "deadline",
                "expires_at",
                "requirements",
            )
            if key in bounty
        }
        raw = json.dumps(relevant, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def changed(self, bounty_id, bounty: dict) -> bool:
        if bounty_id is None:
            return False
        key = str(bounty_id)
        if key not in self.records:
            return False
        return self.records[key] != self.fingerprint(bounty)

    def mark_seen(self, bounty_id, bounty: dict) -> None:
        if bounty_id is not None and str(bounty_id).strip():
            self.records[str(bounty_id)] = self.fingerprint(bounty)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.records, indent=2, sort_keys=True),
            encoding="utf-8",
        )
