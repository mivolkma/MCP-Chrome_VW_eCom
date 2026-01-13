#!/usr/bin/env python
"""Validate processOpportunities payload contains journey-collected information.

Security design:
- Never prints raw payload.
- Redacts URLs and sensitive keys.
- Only reports presence + safe extracted values.

Usage examples:
  python tools/validate_process_opportunities_payload.py --payload <file.json> --email test@test.de --duration 36 --mileage 15000 --down-payment 0
  python tools/validate_process_opportunities_payload.py --payload <file.json> --expect tools/examples/process_expect.example.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SENSITIVE_KEYWORDS = {
    "oneapikey",
    "endpoint",
    "signature",
    "token",
    "authorization",
    "cookie",
    "set-cookie",
    "apikey",
    "api_key",
    "client_secret",
    "password",
    "passwd",
    "secret",
    "id_token",
    "access_token",
    "refresh_token",
}

URL_PREFIXES = ("http://", "https://")


def _is_probably_url(value: str) -> bool:
    return value.startswith(URL_PREFIXES)


def _redact_url(value: str) -> str:
    # Remove query/fragment defensively.
    for sep in ("?", "#"):
        if sep in value:
            value = value.split(sep, 1)[0]
    return value


def _key_is_sensitive(key: str) -> bool:
    k = key.lower().replace("-", "_")
    return any(word in k for word in SENSITIVE_KEYWORDS)


@dataclass
class Finding:
    name: str
    status: str  # PASS/FAIL/WARN
    detail: str


def _walk(obj: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    """Depth-first walk yielding (json_path, value)."""
    yield path, obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            child_path = f"{path}.{k}"
            yield from _walk(v, child_path)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            child_path = f"{path}[{i}]"
            yield from _walk(v, child_path)


def _find_values(payload: Any, predicate) -> list[tuple[str, Any]]:
    hits: list[tuple[str, Any]] = []
    for json_path, value in _walk(payload):
        try:
            if predicate(json_path, value):
                hits.append((json_path, value))
        except Exception:
            continue
    return hits


def _safe_preview(value: Any) -> str:
    """Return a safe-to-log preview of a found value."""
    if value is None:
        return "null"
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, str):
        if _is_probably_url(value):
            return _redact_url(value)
        # avoid dumping potentially sensitive long strings
        if len(value) > 80:
            return f"<string len={len(value)}>"
        return value
    if isinstance(value, list):
        return f"<list len={len(value)}>"
    if isinstance(value, dict):
        return f"<object keys={len(value)}>"
    return f"<{type(value).__name__}>"


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"ERROR: Ungültiges JSON in {path}: {e}")


def _expect_from_file(expect_path: Path) -> dict[str, Any]:
    expect = _load_json(expect_path)
    if not isinstance(expect, dict):
        raise SystemExit("ERROR: --expect muss ein JSON-Objekt sein")
    return expect


def _expect_from_flags(args: argparse.Namespace) -> dict[str, Any]:
    expect: dict[str, Any] = {}
    if args.email:
        expect["email"] = args.email

    finance: dict[str, Any] = {}
    if args.duration is not None:
        finance["duration"] = args.duration
    if args.mileage is not None:
        finance["mileage"] = args.mileage
    if args.down_payment is not None:
        finance["downPayment"] = args.down_payment
    if finance:
        expect["finance"] = finance

    dealer: dict[str, Any] = {}
    if args.dealer_postal_code:
        dealer["postalCode"] = args.dealer_postal_code
    if args.dealer_city:
        dealer["city"] = args.dealer_city
    if dealer:
        expect["dealer"] = dealer

    return expect


def _match_string(payload: Any, expected: str) -> list[tuple[str, Any]]:
    expected_lower = expected.strip().lower()

    def pred(_p: str, v: Any) -> bool:
        return isinstance(v, str) and v.strip().lower() == expected_lower

    return _find_values(payload, pred)


def _match_number(payload: Any, expected: int) -> list[tuple[str, Any]]:
    def pred(_p: str, v: Any) -> bool:
        return isinstance(v, (int, float)) and int(v) == int(expected)

    return _find_values(payload, pred)


def _match_key_value(payload: Any, key_name: str, expected: Any) -> list[tuple[str, Any]]:
    key_lower = key_name.lower()

    def pred(p: str, v: Any) -> bool:
        # Match on path suffix, e.g. $.foo.bar.duration
        if not p.lower().endswith("." + key_lower):
            return False
        if isinstance(expected, str):
            return isinstance(v, str) and v.strip().lower() == expected.strip().lower()
        if isinstance(expected, (int, float)):
            return isinstance(v, (int, float)) and int(v) == int(expected)
        return v == expected

    return _find_values(payload, pred)


def _group_presence_checks(payload: Any) -> list[Finding]:
    """Best-effort presence checks for the major journey groups."""
    findings: list[Finding] = []

    # These are heuristic checks because payload structure varies.
    # We look for key names anywhere in the JSON path.
    def any_path_contains(substrings: list[str]) -> bool:
        subs = [s.lower() for s in substrings]

        def pred(p: str, _v: Any) -> bool:
            p_low = p.lower()
            return any(s in p_low for s in subs)

        return len(_find_values(payload, pred)) > 0

    groups = {
        "Vehicle/Offer": ["vehicle", "offer", "carline", "model", "trim"],
        "Finance": ["duration", "mileage", "downpayment", "recurring", "rate"],
        "Dealer": ["dealer", "partner"],
        "Pickup/Delivery": ["pick", "delivery", "handover", "pickup"],
        "Personal Data": ["firstname", "lastname", "email", "phone", "mobile", "address", "postal", "city", "street"],
        "Consent/Legal": ["consent", "privacy", "datenschutz", "gdpr", "marketing"],
    }

    for group_name, hints in groups.items():
        ok = any_path_contains(hints)
        findings.append(
            Finding(
                name=group_name,
                status="PASS" if ok else "FAIL",
                detail="Felder/Keys im Payload gefunden" if ok else "Keine typischen Keys im Payload gefunden",
            )
        )

    return findings


def _sanitize_payload_inplace(obj: Any) -> Any:
    """Return a redacted copy of the payload for internal searching (not for printing)."""
    if isinstance(obj, dict):
        redacted: dict[str, Any] = {}
        for k, v in obj.items():
            if _key_is_sensitive(k):
                redacted[k] = "[REDACTED]"
            elif isinstance(v, str) and _is_probably_url(v):
                redacted[k] = _redact_url(v)
            else:
                redacted[k] = _sanitize_payload_inplace(v)
        return redacted
    if isinstance(obj, list):
        return [_sanitize_payload_inplace(v) for v in obj]
    if isinstance(obj, str) and _is_probably_url(obj):
        return _redact_url(obj)
    return obj


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate processOpportunities payload completeness")
    parser.add_argument("--payload", required=True, help="Path to redacted processOpportunities payload JSON")

    parser.add_argument("--expect", help="Path to JSON with expected values (safe/dummy only)")

    parser.add_argument("--email", help="Expected email (default: none)")
    parser.add_argument("--duration", type=int, help="Expected duration (months)")
    parser.add_argument("--mileage", type=int, help="Expected yearly mileage")
    parser.add_argument("--down-payment", dest="down_payment", type=int, help="Expected down payment")
    parser.add_argument("--dealer-postal-code", dest="dealer_postal_code", help="Expected dealer postal code")
    parser.add_argument("--dealer-city", dest="dealer_city", help="Expected dealer city")

    args = parser.parse_args()

    payload_path = Path(args.payload)
    if not payload_path.exists():
        print(f"ERROR: Payload-Datei nicht gefunden: {payload_path}", file=sys.stderr)
        return 2

    payload_raw = _load_json(payload_path)
    payload = _sanitize_payload_inplace(payload_raw)

    # Build expectations
    expect: dict[str, Any] = {}
    if args.expect:
        expect.update(_expect_from_file(Path(args.expect)))
    expect.update(_expect_from_flags(args))

    findings: list[Finding] = []
    findings.extend(_group_presence_checks(payload))

    # Value checks (optional)
    email_expected = expect.get("email")
    if email_expected:
        hits = _match_string(payload, str(email_expected))
        findings.append(
            Finding(
                name="Email value",
                status="PASS" if hits else "FAIL",
                detail=(
                    f"Gefunden an {hits[0][0]} = {_safe_preview(hits[0][1])}" if hits else "E-Mail Wert nicht gefunden"
                ),
            )
        )

    finance_expect = expect.get("finance") if isinstance(expect.get("finance"), dict) else {}
    if finance_expect:
        for k in ("duration", "mileage", "downPayment"):
            if k in finance_expect:
                hits = _match_key_value(payload, k, finance_expect[k])
                # Fallback: match by value only
                if not hits and isinstance(finance_expect[k], (int, float)):
                    hits = _match_number(payload, int(finance_expect[k]))
                findings.append(
                    Finding(
                        name=f"Finance {k}",
                        status="PASS" if hits else "FAIL",
                        detail=(
                            f"Gefunden an {hits[0][0]} = {_safe_preview(hits[0][1])}" if hits else "Wert nicht gefunden"
                        ),
                    )
                )

    dealer_expect = expect.get("dealer") if isinstance(expect.get("dealer"), dict) else {}
    if dealer_expect:
        for k in ("postalCode", "city"):
            if k in dealer_expect:
                hits = _match_key_value(payload, k, dealer_expect[k])
                if not hits and isinstance(dealer_expect[k], str):
                    hits = _match_string(payload, dealer_expect[k])
                findings.append(
                    Finding(
                        name=f"Dealer {k}",
                        status="PASS" if hits else "FAIL",
                        detail=(
                            f"Gefunden an {hits[0][0]} = {_safe_preview(hits[0][1])}" if hits else "Wert nicht gefunden"
                        ),
                    )
                )

    # Print report
    print("processOpportunities payload validation (safe summary)")
    print("Payload:", payload_path)
    print()

    max_name = max(len(f.name) for f in findings) if findings else 10
    failed = 0
    warned = 0
    for f in findings:
        if f.status == "FAIL":
            failed += 1
        elif f.status == "WARN":
            warned += 1
        print(f"- {f.name.ljust(max_name)}  {f.status}: {f.detail}")

    print()
    if failed:
        print(f"RESULT: FAIL ({failed} fehlgeschlagen, {warned} Warnungen)")
        return 1
    print(f"RESULT: PASS ({warned} Warnungen)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
