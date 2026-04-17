#!/usr/bin/env python3
"""
update_readme.py
----------------
Fetches the latest public GitHub activity for rubak714 and injects it
into the README.md between <!-- ACTIVITY:START --> and <!-- ACTIVITY:END -->.

Env vars:
  GITHUB_TOKEN    — classic PAT with read:user scope (set in repo secrets)
  GITHUB_USERNAME — defaults to rubak714
"""

import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

USERNAME = os.getenv("GITHUB_USERNAME", "rubak714")
TOKEN    = os.getenv("GITHUB_TOKEN", "")
README   = Path("README.md")
HEADERS  = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

EVENT_MAP = {
    "PushEvent":         "📦 Pushed to",
    "CreateEvent":       "🌿 Created branch/tag in",
    "PullRequestEvent":  "🔀 Opened a pull request in",
    "IssuesEvent":       "💬 Opened an issue in",
    "WatchEvent":        "⭐ Starred",
    "ForkEvent":         "🍴 Forked",
    "IssueCommentEvent": "🗣️  Commented in",
    "ReleaseEvent":      "🚀 Released in",
    "DeleteEvent":       "🗑️  Deleted ref in",
}


def fetch_events(n: int = 15) -> list[dict]:
    url = f"https://api.github.com/users/{USERNAME}/events/public?per_page={n}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def render_event(evt: dict) -> str | None:
    label = EVENT_MAP.get(evt.get("type", ""))
    if not label:
        return None
    repo = evt.get("repo", {}).get("name", "unknown/unknown")
    date = evt.get("created_at", "")[:10]
    return f"- {label} **[{repo}](https://github.com/{repo})** `{date}`"


def build_block(events: list[dict]) -> str:
    lines: list[str] = []
    for evt in events:
        line = render_event(evt)
        if line and line not in lines:
            lines.append(line)
        if len(lines) >= 5:
            break

    ts     = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = f"#### ⚡ Recent Activity\n\n<!-- last refreshed: {ts} -->\n"
    body   = "\n".join(lines) if lines else "_No recent public activity._"
    return header + body


def inject(content: str, block: str) -> str:
    marker = r"<!-- ACTIVITY:START -->.*?<!-- ACTIVITY:END -->"
    replacement = f"<!-- ACTIVITY:START -->\n{block}\n<!-- ACTIVITY:END -->"
    updated, n = re.subn(marker, replacement, content, flags=re.DOTALL)
    if n == 0:
        updated = content + f"\n\n{replacement}\n"
    return updated


def main() -> None:
    if not README.exists():
        raise FileNotFoundError("README.md not found — run from the repo root.")

    print(f"🔍  Fetching activity for @{USERNAME} …")
    events  = fetch_events()
    block   = build_block(events)
    content = README.read_text(encoding="utf-8")
    updated = inject(content, block)
    README.write_text(updated, encoding="utf-8")
    print("✅  README.md updated.")


if __name__ == "__main__":
    main()
