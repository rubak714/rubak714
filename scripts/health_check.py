#!/usr/bin/env python3
"""
health_check.py
---------------
Checks a set of public IT/cloud service endpoints and writes:
  - docs/health_report.json   (machine-readable JSON report)
  - assets/health_badge.svg   (SVG status badge for README)

Demonstrates: Python scripting, REST API calls, JSON output,
              error handling — skills used daily in IT/SysAdmin/SOC roles.

Run locally : python scripts/health_check.py
Run in CI   : triggered by .github/workflows/health-check.yml
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── Services to monitor ───────────────────────────────────────────────────────
TARGETS = [
    {"name": "GitHub API",         "url": "https://api.github.com",                    "expect": 200},
    {"name": "Azure Status",       "url": "https://status.azure.com/en-us/status",     "expect": 200},
    {"name": "Microsoft 365",      "url": "https://portal.office.com",                 "expect": 200},
    {"name": "AWS Health",         "url": "https://health.aws.amazon.com/health/status","expect": 200},
    {"name": "GCP Status",         "url": "https://status.cloud.google.com",           "expect": 200},
    {"name": "Splunk Docs",        "url": "https://docs.splunk.com",                   "expect": 200},
    {"name": "LinkedIn Profile",   "url": "https://www.linkedin.com/in/rubk/",         "expect": 200},
]

TIMEOUT     = 10
REPORT_PATH = Path("docs/health_report.json")
BADGE_PATH  = Path("assets/health_badge.svg")


# ── Check one endpoint ────────────────────────────────────────────────────────

def check(target: dict) -> dict:
    t0 = time.monotonic()
    try:
        r = requests.get(
            target["url"], timeout=TIMEOUT, allow_redirects=True,
            headers={"User-Agent": "rubak714-health-checker/2.0"},
        )
        ms = round((time.monotonic() - t0) * 1000)
        return {
            "name":       target["name"],
            "url":        target["url"],
            "http_status": r.status_code,
            "ok":         r.status_code == target["expect"],
            "latency_ms": ms,
        }
    except requests.RequestException as exc:
        ms = round((time.monotonic() - t0) * 1000)
        return {
            "name":       target["name"],
            "url":        target["url"],
            "http_status": None,
            "ok":         False,
            "latency_ms": ms,
            "error":      str(exc),
        }


# ── Build SVG status badge ────────────────────────────────────────────────────

def build_badge(all_ok: bool) -> str:
    colour = "#a6e3a1" if all_ok else "#f38ba8"
    text   = "all systems ✓" if all_ok else "degraded ✗"
    w_l, w_r = 52, 116
    w = w_l + w_r
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20">'
        f'<rect rx="3" width="{w}" height="20" fill="#555"/>'
        f'<rect rx="3" x="{w_l}" width="{w_r}" height="20" fill="{colour}"/>'
        f'<rect x="{w_l}" width="4" height="20" fill="{colour}"/>'
        f'<g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,sans-serif" font-size="11">'
        f'<text x="{w_l//2}" y="14">infra</text>'
        f'<text x="{w_l + w_r//2}" y="14" fill="#1e1e2e">{text}</text>'
        f"</g></svg>"
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("🏥  Running infrastructure health checks …\n")

    results = [check(t) for t in TARGETS]
    all_ok  = all(r["ok"] for r in results)

    for r in results:
        icon = "✅" if r["ok"] else "❌"
        status = r.get("http_status") or "ERR"
        print(f"  {icon}  {r['name']:<22}  HTTP {status:<4}  {r['latency_ms']} ms")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "all_ok":        all_ok,
        "passed":        sum(1 for r in results if r["ok"]),
        "failed":        sum(1 for r in results if not r["ok"]),
        "results":       results,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    BADGE_PATH.parent.mkdir(parents=True, exist_ok=True)

    REPORT_PATH.write_text(json.dumps(report, indent=2))
    BADGE_PATH.write_text(build_badge(all_ok))

    print(f"\n📄  Report → {REPORT_PATH}")
    print(f"🏷️   Badge  → {BADGE_PATH}")
    print(f"\n{'✅  All checks passed.' if all_ok else '⚠️  Some checks failed — review report.'}")

    if not all_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
