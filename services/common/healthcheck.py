from __future__ import annotations

import sys

import httpx


def main() -> int:
    try:
        response = httpx.get("http://127.0.0.1:8000/health", timeout=3)
        response.raise_for_status()
    except Exception:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

