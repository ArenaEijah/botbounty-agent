from __future__ import annotations

import json
from pathlib import Path


class BountyHistory:
    def __init__(self, path: str = ".agent_state/history.json"):
        self.path = Path(path)
        self.seen: set[str] = set()
        self._load()

    def _load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, ValueError):
            return

        if isinstance(data, list):
            self.seen = {str(item) for item in data if str(item).strip()}

    def contains(self, bounty_id) -> bool:
        if bounty_id is None:
            return False
        return str(bounty_id) in self.seen

    def mark_seen(self, bounty_id) -> None:
        if bounty_id is not None and str(bounty_id).strip():
            self.seen.add(str(bounty_id))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(sorted(self.seen), indent=2),
            encoding="utf-8",
        )
