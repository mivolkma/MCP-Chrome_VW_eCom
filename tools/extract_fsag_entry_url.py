#!/usr/bin/env python
"""Extract FSAG journey entry URL from DUC leasing response JSON.

Why:
- Für den manuellen Test (VPN + Browser) wird häufig der ENTRY_POINT/Continue-Link aus der DUC-Response benötigt.

Security:
- Standardmäßig wird die URL **redacted** ausgegeben (Query/Fragment entfernt).
- Für den lokalen manuellen Test kann die volle URL via `--full` ausgegeben werden.
- Das Tool schreibt nichts in Git/Repo – nur stdout.

Examples:
  python tools/extract_fsag_entry_url.py --input results/.../duc_leasing_response.json
  python tools/extract_fsag_entry_url.py --input results/.../duc_leasing_response.json --full
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

URL_PREFIXES = ("http://", "https://")


def _is_url(value: str) -> bool:
    return value.startswith(URL_PREFIXES)


def _redact_url(url: str) -> str:
    for sep in ("?", "#"):
        if sep in url:
            url = url.split(sep, 1)[0]
    return url


def _walk(obj: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"ERROR: Datei nicht gefunden: {path}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"ERROR: Ungültiges JSON in {path}: {e}")


def _extract_candidate_urls(payload: Any) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    for p, v in _walk(payload):
        if isinstance(v, str) and _is_url(v):
            candidates.append((p, v))
    return candidates


def _score(path: str, url: str) -> int:
    """Heuristic scoring to pick the most likely FSAG entry URL."""
    score = 0
    p = path.lower()
    u = url.lower()

    # Prefer explicit link names
    if any(token in p for token in ("entry_point", "entrypoint", "entry", "continue_in_checkout", "continue")):
        score += 50

    # Prefer FSAG/checkout-ish URLs if present
    if "fsag" in u:
        score += 20
    if "checkout" in u:
        score += 10
    if "leasing" in u:
        score += 5

    # Prefer URLs with query (often contains token) for full mode; still valid
    if "?" in url:
        score += 2

    return score


def _pick_best(candidates: list[tuple[str, str]]) -> tuple[str, str] | None:
    if not candidates:
        return None
    ranked = sorted(candidates, key=lambda x: _score(x[0], x[1]), reverse=True)
    return ranked[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract FSAG entry URL from DUC leasing response JSON")
    parser.add_argument("--input", required=True, help="Path to DUC leasing response JSON")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Print full URL including query/fragment (use locally; do not commit/log)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Print all found URLs (useful for debugging); still redacted unless --full",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    payload = _load_json(input_path)

    candidates = _extract_candidate_urls(payload)
    if not candidates:
        print("ERROR: Keine URLs im JSON gefunden.", file=sys.stderr)
        return 2

    def fmt(url: str) -> str:
        return url if args.full else _redact_url(url)

    if args.all:
        print("Found URLs (best-effort):")
        for p, u in sorted(candidates, key=lambda x: _score(x[0], x[1]), reverse=True):
            print(f"- {p}: {fmt(u)}")
        return 0

    best = _pick_best(candidates)
    if not best:
        print("ERROR: Keine passende URL gefunden.", file=sys.stderr)
        return 2

    best_path, best_url = best
    print(fmt(best_url))

    # If redacted mode, show a hint that full is available
    if not args.full and ("?" in best_url or "#" in best_url):
        print("\nHinweis: Für den lokalen VPN-Manuallauf ggf. `--full` nutzen (nicht committen/loggen).", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
