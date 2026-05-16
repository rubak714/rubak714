#!/usr/bin/env python3
"""
Infrastructure Health Check
Checks availability of key profile endpoints and writes a JSON report.
Always exits with code 0 so the GitHub Actions workflow never fails.
"""

import json
import os
import sys
import datetime
import urllib.request
import urllib.error

CHECKS = [
    {"name": "GitHub Profile",        "url": "https://github.com/rubak714"},
    {"name": "LinkedIn",              "url": "https://www.linkedin.com/in/rubkp110/"},
    {"name": "TryHackMe",            "url": "https://tryhackme.com/p/Birdybird00"},
    {"name": "Credly",               "url": "https://www.credly.com/users/rubaiya110/badges"},
    {"name": "Enterprise AD Lab",    "url": "https://github.com/rubak714/enterprise-helpdesk-ad-lab"},
    {"name": "DevOps Platform",      "url": "https://github.com/rubak714/devops-production-platform"},
]

TIMEOUT = 10


def check_url(name: str, url: str) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            status = resp.status
            ok = status < 400
    except urllib.error.HTTPError as e:
        status = e.code
        ok = status < 400
    except Exception as e:
        status = 0
        ok = False

    return {
        "name": name,
        "url": url,
        "status": status,
        "healthy": ok,
        "checked_at": datetime.datetime.utcnow().isoformat() + "Z",
    }


def main():
    results = [check_url(c["name"], c["url"]) for c in CHECKS]

    healthy = sum(1 for r in results if r["healthy"])
    total = len(results)

    report = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "summary": {
            "healthy": healthy,
            "total": total,
            "status": "healthy" if healthy == total else "degraded" if healthy > 0 else "down",
        },
        "checks": results,
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/health_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print(f"\n{'='*50}")
    print(f"  Infrastructure Health Check — {report['summary']['status'].upper()}")
    print(f"  {healthy}/{total} endpoints reachable")
    print(f"{'='*50}")
    for r in results:
        icon = "✅" if r["healthy"] else "⚠️ "
        print(f"  {icon}  {r['name']} ({r['status']})")
    print()

    # Always exit 0 — health degradation is informational, not a workflow failure
    sys.exit(0)


if __name__ == "__main__":
    main()