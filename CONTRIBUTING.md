# Contributing

This is a personal profile repository. Suggestions, spotted bugs in the scripts, or ideas for new automation are very welcome.

## Local setup

```bash
git clone https://github.com/rubak714/rubak714.git
cd rubak714
pip install -r requirements.txt
```

## Running scripts locally

```bash
# Health check — no token needed
python scripts/health_check.py

# README updater — needs a GitHub token
export GITHUB_TOKEN=ghp_yourtoken
python scripts/update_readme.py
```

## Code style
- Python: PEP 8, type hints, docstrings on public functions
- YAML: 2-space indent, comments on non-obvious keys
- No secrets or credentials committed
