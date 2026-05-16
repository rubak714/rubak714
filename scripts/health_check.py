#!/usr/bin/env python3
"""
Profile Health Check — stdlib only, always exits 0.
Writes docs/health_report.json so the workflow can upload it as an artifact.
"""
import json, os, sys, datetime, urllib.request, urllib.error

CHECKS = [
    {"name": "GitHub Profile",      "url": "https://github.com/rubak714"},
    {"name": "Azure IaC Foundation","url": "https://github.com/rubak714/azure-iac-foundation"},
    {"name": "Enterprise AD Lab",   "url": "https://github.com/rubak714/enterprise-helpdesk-ad-lab"},
    {"name": "DevOps Platform",     "url": "https://github.com/rubak714/devops-production-platform"},
    {"name": "TryHackMe Profile",   "url": "https://tryhackme.com/p/Birdybird00"},
]
TIMEOUT = 12

def check_url(name, url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return {"name": name, "url": url, "status": r.status,
                    "healthy": r.status < 400,
                    "checked_at": datetime.datetime.utcnow().isoformat() + "Z"}
    except urllib.error.HTTPError as e:
        return {"name": name, "url": url, "status": e.code,
                "healthy": e.code < 400,
                "checked_at": datetime.datetime.utcnow().isoformat() + "Z"}
    except Exception:
        return {"name": name, "url": url, "status": 0, "healthy": False,
                "checked_at": datetime.datetime.utcnow().isoformat() + "Z"}

def main():
    results = [check_url(c["name"], c["url"]) for c in CHECKS]
    ok = sum(1 for r in results if r["healthy"])
    report = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "summary": {"healthy": ok, "total": len(results),
                    "status": "healthy" if ok == len(results) else "degraded" if ok else "down"},
        "checks": results,
    }
    os.makedirs("docs", exist_ok=True)
    with open("docs/health_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nHealth Check: {report['summary']['status'].upper()}  ({ok}/{len(results)} reachable)")
    for r in results:
        print(f"  {'OK' if r['healthy'] else '--'}  {r['name']}  [{r['status']}]")
    sys.exit(0)   # always 0 — degradation is informational

if __name__ == "__main__":
    main()