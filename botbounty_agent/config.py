from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Config:
    api_base: str = os.getenv("BOTBOUNTY_API_BASE", "https://botbounty-production.up.railway.app/api")
    dry_run: bool = os.getenv("AGENT_DRY_RUN", "true").lower() not in {"0", "false", "no"}
    min_bounty_usd: float = float(os.getenv("MIN_BOUNTY_USD", "1"))
