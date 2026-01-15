import argparse
import datetime as _dt
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup


# Make console output robust on Windows when stdout is redirected.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


_NET_SENSITIVE_KEYWORDS = {
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

_NET_PII_KEYWORDS = {
    "email",
    "e_mail",
    "first",
    "firstname",
    "first_name",
    "last",
    "lastname",
    "last_name",
    "phone",
    "mobile",
    "tel",
}


def _net_key_is_sensitive(key: str) -> bool:
    k = (key or "").lower().replace("-", "_")
    return any(word in k for word in _NET_SENSITIVE_KEYWORDS)


def _net_key_looks_pii(key: str) -> bool:
    k = (key or "").lower().replace("-", "_")
    return any(word in k for word in _NET_PII_KEYWORDS)


def _sha256_str(value: str) -> str:
    try:
        return hashlib.sha256((value or "").encode("utf-8")).hexdigest()
    except Exception:
        return ""


def _redact_url_value(value: str) -> str:
    if not isinstance(value, str):
        return value
    if not (value.startswith("http://") or value.startswith("https://")):
        return value
    # Strip query/fragment defensively.
    for sep in ("?", "#"):
        if sep in value:
            value = value.split(sep, 1)[0]
    return value


def _redact_payload(obj):
    """Redacts sensitive keys and URL values in a JSON-like structure.

    Security rules:
    - never persist cookies/authorization/tokens
    - strip query/fragment from URLs
    """
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if _net_key_is_sensitive(str(k)):
                out[k] = "[REDACTED]"
            elif isinstance(v, str):
                if _net_key_looks_pii(str(k)):
                    out[k] = {"_sha256": _sha256_str(v), "_len": len(v)}
                else:
                    out[k] = _redact_url_value(v)
            else:
                out[k] = _redact_payload(v)
        return out
    if isinstance(obj, list):
        return [_redact_payload(v) for v in obj]
    if isinstance(obj, str):
        return _redact_url_value(obj)
    return obj


def _net_headers_redacted(headers: dict | None) -> dict:
    if not isinstance(headers, dict):
        return {}
    out: dict = {}
    for k, v in headers.items():
        if _net_key_is_sensitive(str(k)):
            out[k] = "[REDACTED]"
        else:
            # Keep small safe headers only; avoid huge/PII-heavy values.
            if isinstance(v, str) and len(v) > 200:
                out[k] = f"<string len={len(v)}>"
            else:
                out[k] = v
    return out


def _append_jsonl(path: Path, record: dict) -> None:
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Best-effort; never break the test run due to logging.
        pass


def _now_run_id() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def prepare_run_paths(
    *,
    results_root: Path,
    run_id: str | None,
    charter_file: Path,
    start_url: str,
    report_file: Path | None,
    screenshots_dir: Path | None,
) -> tuple[Path, Path, Path]:
    """Prepares a run directory, report path, and screenshots directory.

    If report_file/screenshots_dir are provided, they are respected.
    Otherwise we create results_root/<run_id>/ with a default report and screenshots/.
    """
    results_root = Path(results_root)
    charter_file = Path(charter_file)

    if report_file and screenshots_dir:
        run_dir = Path(report_file).parent
        Path(screenshots_dir).mkdir(parents=True, exist_ok=True)
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir, Path(report_file), Path(screenshots_dir)

    rid = run_id or _now_run_id()
    run_dir = results_root / rid
    screenshots_dir = run_dir / "screenshots"
    report_file = run_dir / "BTO_Test_Report_v1.0.html"

    run_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    # Snapshot inputs (safe/redacted): charter + URL without query/fragment.
    inputs_dir = run_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copyfile(charter_file, inputs_dir / charter_file.name)
    except Exception:
        pass
    try:
        (inputs_dir / "start_url_redacted.txt").write_text(
            redact_url_for_logging(start_url),
            encoding="utf-8",
        )
    except Exception:
        pass

    return run_dir, report_file, screenshots_dir


def write_run_meta(run_dir: Path, *, url: str, charter_file: Path, started_at: str, finished_at: str, totals: dict) -> None:
    meta = {
        "started_at": started_at,
        "finished_at": finished_at,
        "url": redact_url_for_logging(url),
        "charter_file": str(Path(charter_file).as_posix()),
        "python": sys.version,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
        },
        "totals": totals,
    }
    (Path(run_dir) / "run_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def classify_finding(*, message: str, is_timeout: bool, is_error_page: bool) -> tuple[str, str]:
    """Returns (kind, severity).

    kind: 'APP' or 'SCRIPT'
    severity: 'critical'|'high'|'medium'|'low'
    """
    if is_error_page:
        return "APP", "critical"
    if is_timeout:
        return "SCRIPT", "medium"
    msg = (message or "").lower()
    if "critical error: detected" in msg and ("401" in msg or "403" in msg or "404" in msg):
        return "APP", "critical"
    if "could not find element" in msg:
        return "SCRIPT", "medium"
    return "SCRIPT", "low"


def write_findings(run_dir: Path, *, findings: list[dict], report_file: Path) -> None:
    run_dir = Path(run_dir)
    (run_dir / "findings.json").write_text(json.dumps(findings, ensure_ascii=False, indent=2), encoding="utf-8")

    app_findings = [f for f in findings if f.get("kind") == "APP"]
    script_findings = [f for f in findings if f.get("kind") == "SCRIPT"]

    lines = [
        "# Findings",
        "",
        f"- Report: {Path(report_file).name}",
        "",
        "## Echte Findings (APP)",
        "",
    ]
    if not app_findings:
        lines.append("- Keine echten App-Findings erkannt (nur Script-/Locator-Themen oder alles grün).")
    else:
        for f in app_findings:
            lines.append(f"- [{f.get('severity')}] {f.get('case_id')} Step {f.get('step_num')}: {f.get('summary')}")

    lines += ["", "## Script-Issues (zum Reparieren)", ""]
    if not script_findings:
        lines.append("- Keine Script-Issues.")
    else:
        for f in script_findings:
            lines.append(f"- [{f.get('severity')}] {f.get('case_id')} Step {f.get('step_num')}: {f.get('summary')}")

    (run_dir / "findings.md").write_text("\n".join(lines), encoding="utf-8")


def write_summary(run_dir: Path, *, totals: dict, report_file: Path) -> None:
    lines = [
        "# Run Summary",
        "",
        f"- Report: {Path(report_file).name}",
        f"- Steps: {totals.get('steps_total', 0)} (Pass={totals.get('pass', 0)} Warn={totals.get('warn', 0)} Fail={totals.get('fail', 0)})",
        "",
        "Artefakte:",
        f"- {Path(report_file).name}",
        "- screenshots/",
        "- network_trace.jsonl",
        "- technical_checkpoints.md / technical_checkpoints.json",
        "- dataflow_inventory.md / dataflow_inventory.json",
        "- findings.md / findings.json",
        "- run_meta.json",
    ]

    after_login_snapshot = Path(run_dir) / "form_snapshot_after_login.json"
    if after_login_snapshot.exists():
        lines.append("- form_snapshot_after_login.json")

    login_verification = Path(run_dir) / "login_verification.json"
    if login_verification.exists():
        lines.append("- login_verification.json")
    (Path(run_dir) / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_dataflow_inventory(run_dir: Path) -> None:
    """Creates a per-run dataflow inventory based on captured network trace.

    Goal: At the start of a journey (i.e., earliest available evidence), automatically
    create a best-effort overview of which backend-ish services/endpoints were called.

    Outputs (in run_dir):
    - dataflow_inventory.json
    - dataflow_inventory.md (includes a Mermaid flowchart)

    Notes:
    - Uses `network_trace.jsonl`, which already contains redacted URLs.
    - Does not persist cookies/auth or plaintext PII.
    """
    run_dir = Path(run_dir)
    net_path = run_dir / "network_trace.jsonl"
    events = _read_jsonl(net_path)

    def service_for_url(url: str) -> str:
        ul = (url or "").lower()
        if "/app/authproxy/" in ul or "authproxy" in ul:
            # Be explicit for the known endpoints (useful for prefill/identity reasoning)
            if "authenticated" in ul:
                return "authproxy/authenticated"
            if "/user" in ul:
                return "authproxy/user"
            return "authproxy"
        if "processopportunities" in ul:
            return "processOpportunities"
        if "duc-leasing" in ul:
            return "duc-leasing"
        if "/bff-forms/" in ul:
            return "bff-forms"
        if "/bff/" in ul:
            return "bff"
        if "chosenvehicle" in ul or "chosen-vehicle" in ul:
            return "chosenVehicle"
        if "pickuplocation" in ul or "pickup-location" in ul:
            return "pickupLocation"
        if "/pickup" in ul:
            return "pickup"
        if "sds" in ul or "dealer" in ul:
            return "dealer/sds"

        # Fallback: group by host if parsable.
        try:
            host = urlsplit(url or "").netloc
            if host:
                return f"host:{host.lower()}"
        except Exception:
            pass
        return "other"

    services: dict[str, dict] = {}
    non_2xx: list[dict] = []
    hosts: dict[str, int] = {}

    for ev in events:
        if not isinstance(ev, dict):
            continue
        if ev.get("type") != "response":
            continue

        url = str(ev.get("url") or "")
        svc = service_for_url(url)

        try:
            status_i = int(ev.get("status"))
        except Exception:
            status_i = -1

        try:
            host = urlsplit(url).netloc.lower()
        except Exception:
            host = ""
        if host:
            hosts[host] = int(hosts.get(host, 0)) + 1

        st = services.setdefault(
            svc,
            {
                "hits": 0,
                "statuses": {},
                "examples": [],
                "steps": [],
                "all_2xx": True,
            },
        )
        st["hits"] += 1
        st_statuses = st["statuses"]
        st_statuses[str(status_i)] = int(st_statuses.get(str(status_i), 0)) + 1
        step = ev.get("step")
        if step and step not in st["steps"] and len(st["steps"]) < 12:
            st["steps"].append(step)
        if len(st["examples"]) < 4 and url:
            st["examples"].append(url)
        if not (200 <= status_i <= 299):
            st["all_2xx"] = False
            non_2xx.append({"service": svc, "status": status_i, "url": url, "step": step})

    report = {
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "network_trace": str(net_path.name),
        "hosts": dict(sorted(hosts.items(), key=lambda kv: kv[1], reverse=True)[:20]),
        "services": services,
        "non_2xx": non_2xx,
    }

    (run_dir / "dataflow_inventory.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Mermaid diagram: show only discovered services
    def node_id(name: str) -> str:
        # Mermaid id must be simple; keep stable across runs.
        return "N_" + re.sub(r"[^a-zA-Z0-9_]", "_", name)

    discovered = [k for k, v in services.items() if isinstance(v, dict) and int(v.get("hits") or 0) > 0]
    discovered_sorted = sorted(discovered)

    mermaid: list[str] = [
        "flowchart LR",
        "  FE[Checkout Frontend]",
    ]
    for svc in discovered_sorted:
        nid = node_id(svc)
        label = svc
        mermaid.append(f"  {nid}[{label}]")
        mermaid.append(f"  FE --> {nid}")

    md: list[str] = [
        "# Dataflow Inventory",
        "",
        "Ziel: Automatische Bestandsaufnahme des realen Datenflusses (aus dem Network-Trace) pro Run.",
        "",
        f"Quelle: {net_path.name}",
        "",
        "## Überblick (Services/Endpoints)",
        "",
    ]
    if not services:
        md.append("- Keine backend-ish Responses im Trace erkannt (Run evtl. sehr kurz oder Filter zu eng).")
    else:
        for svc in sorted(services.keys()):
            st = services[svc]
            ok = st.get("all_2xx") is True
            md.append(
                f"- {svc}: {'PASS' if ok else 'FAIL'} (hits={st.get('hits', 0)}, statuses={st.get('statuses', {})})"
            )
            for ex in st.get("examples", []) or []:
                md.append(f"  - example: {ex}")

    md += [
        "",
        "## Mermaid (best-effort)",
        "",
        "```mermaid",
        *mermaid,
        "```",
    ]

    (run_dir / "dataflow_inventory.md").write_text("\n".join(md), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict]:
    out: list[dict] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = (line or "").strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        out.append(obj)
                except Exception:
                    continue
    except Exception:
        return []
    return out


def _recursive_find_keys(obj, *, key_predicate) -> list[tuple[str, object]]:
    found: list[tuple[str, object]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            try:
                ks = str(k)
            except Exception:
                ks = ""
            if key_predicate(ks):
                found.append((ks, v))
            found.extend(_recursive_find_keys(v, key_predicate=key_predicate))
    elif isinstance(obj, list):
        for v in obj:
            found.extend(_recursive_find_keys(v, key_predicate=key_predicate))
    return found


def _safe_read_json(path: Path) -> object | None:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return None


def write_technical_checkpoints(run_dir: Path) -> list[dict]:
    """Creates technical checkpoint artefacts based on captured network + api files.

    Outputs (in run_dir):
    - technical_checkpoints.json
    - technical_checkpoints.md

    Returns: findings to append.
    """
    run_dir = Path(run_dir)
    net_path = run_dir / "network_trace.jsonl"
    api_dir = run_dir / "api"

    events = _read_jsonl(net_path)

    # Order matters: more specific buckets first.
    buckets = {
        "processOpportunities": ["processopportunities"],
        "duc-leasing": ["duc-leasing"],
        "dealer/sds": ["sds", "dealer"],
        "pickupLocation": ["pickuplocation", "pickup-location"],
        "pickup": ["/pickup"],
        "chosenVehicle": ["chosenvehicle", "chosen-vehicle"],
        # Generic backend buckets to make short runs useful.
        "bff-forms": ["/bff-forms/"],
        "bff": ["/bff/"],
    }

    def bucket_for_url(url: str) -> str | None:
        ul = (url or "").lower()
        for name, pats in buckets.items():
            if any(p in ul for p in pats):
                return name
        return None

    endpoint_stats: dict[str, dict] = {}
    non_2xx: list[dict] = []

    for ev in events:
        if ev.get("type") != "response":
            continue
        url = str(ev.get("url") or "")
        bucket = bucket_for_url(url)
        if not bucket:
            continue
        status = ev.get("status")
        try:
            status_i = int(status)
        except Exception:
            status_i = -1

        st = endpoint_stats.setdefault(
            bucket,
            {"hits": 0, "statuses": {}, "all_2xx": True, "examples": []},
        )
        st["hits"] += 1
        st_statuses = st["statuses"]
        st_statuses[str(status_i)] = int(st_statuses.get(str(status_i), 0)) + 1
        if len(st["examples"]) < 3:
            st["examples"].append(url)
        if not (200 <= status_i <= 299):
            st["all_2xx"] = False
            non_2xx.append({"bucket": bucket, "status": status_i, "url": url, "step": ev.get("step")})

    proc_payload = run_dir / "processOpportunities_payload_redacted.json"
    proc_resp = run_dir / "processOpportunities_response_redacted.json"
    duc_resp = run_dir / "duc_leasing_response.json"
    duc_req = run_dir / "duc_leasing_request_redacted.json"

    duc_obj = _safe_read_json(duc_resp) if duc_resp.exists() else None
    proc_payload_obj = _safe_read_json(proc_payload) if proc_payload.exists() else None

    duc_links: dict[str, str] = {}
    duc_token_present = False
    if duc_obj is not None:
        def is_link_key(k: str) -> bool:
            kl = (k or "").lower()
            return ("entry" in kl and "point" in kl) or ("continue" in kl and "checkout" in kl) or ("url" in kl and "checkout" in kl)

        for k, v in _recursive_find_keys(duc_obj, key_predicate=is_link_key):
            if isinstance(v, str) and (v.startswith("http://") or v.startswith("https://")):
                duc_links[k] = redact_url_for_logging(v)

        def is_token_key(k: str) -> bool:
            return "token" in (k or "").lower()

        duc_token_present = len(_recursive_find_keys(duc_obj, key_predicate=is_token_key)) > 0

    chosen_vehicle: dict[str, object] = {}
    if api_dir.exists():
        # Best-effort: take the latest captured response
        matches = sorted(api_dir.glob("chosenVehicle_response_*.json"))
        if matches:
            obj = _safe_read_json(matches[-1])
            if isinstance(obj, dict):
                for key in ("modelCode", "modelcode", "model", "derivative", "derivate", "vehicleId", "vehicle_id"):
                    if key in obj:
                        chosen_vehicle[key] = obj.get(key)

    report = {
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "network_trace": str(net_path.name),
        "endpoints": endpoint_stats,
        "non_2xx": non_2xx,
        "processOpportunities": {
            "payload_file": proc_payload.name if proc_payload.exists() else None,
            "response_file": proc_resp.name if proc_resp.exists() else None,
            "payload_keys": sorted(list(proc_payload_obj.keys())) if isinstance(proc_payload_obj, dict) else None,
        },
        "ducLeasing": {
            "request_file": duc_req.name if duc_req.exists() else None,
            "response_file": duc_resp.name if duc_resp.exists() else None,
            "continuation_links": duc_links,
            "token_present": duc_token_present,
        },
        "chosenVehicle": chosen_vehicle or None,
    }

    (run_dir / "technical_checkpoints.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    md: list[str] = [
        "# Technical Checkpoints",
        "",
        "Ziel: DevTools-ähnliche Nachvollziehbarkeit (Frontend→Backend Calls + Artefakte) pro Run.",
        "",
        "## 1) Call Health (2xx)",
        "",
    ]
    if not endpoint_stats:
        md.append("- Keine relevanten Endpoints im Trace erkannt (Run zu kurz oder Filter zu eng).")
    else:
        for name in sorted(endpoint_stats.keys()):
            st = endpoint_stats[name]
            ok = st.get("all_2xx") is True
            hits = st.get("hits", 0)
            md.append(f"- {name}: {'PASS' if ok else 'FAIL'} (hits={hits}, statuses={st.get('statuses', {})})")
            for ex in st.get("examples", []) or []:
                md.append(f"  - example: {ex}")

    md += [
        "",
        "## 2) processOpportunities (Payload/Response)",
        "",
        f"- Payload: {proc_payload.name if proc_payload.exists() else 'nicht erfasst'}",
        f"- Response: {proc_resp.name if proc_resp.exists() else 'nicht erfasst'}",
        "",
        "## 3) duc-leasing (Journey Fortsetzung)",
        "",
        f"- Request: {duc_req.name if duc_req.exists() else 'nicht erfasst'}",
        f"- Response: {duc_resp.name if duc_resp.exists() else 'nicht erfasst'}",
        f"- Token vorhanden (nur Presence): {str(duc_token_present)}",
    ]
    if duc_links:
        md.append("- Continuation Links (redacted):")
        for k, v in duc_links.items():
            md.append(f"  - {k}: {v}")
    else:
        md.append("- Continuation Links: nicht gefunden (Run evtl. vor diesem Schritt abgebrochen).")

    md += [
        "",
        "## 4) Dealer/Pickup/ChosenVehicle (Evidence)",
        "",
        "Diese Prüfung ist aktuell evidence-basiert: Backend-Responses werden (redacted) abgelegt; UI-Abgleich erfolgt via Screenshots/Report.",
        "",
        f"- api/: {'vorhanden' if api_dir.exists() else 'nicht vorhanden'}",
    ]
    if chosen_vehicle:
        md.append(f"- chosenVehicle (best-effort extract): {chosen_vehicle}")

    (run_dir / "technical_checkpoints.md").write_text("\n".join(md), encoding="utf-8")

    findings: list[dict] = []
    for item in non_2xx:
        try:
            status_i = int(item.get("status"))
        except Exception:
            continue
        if status_i >= 500:
            findings.append(
                {
                    "kind": "APP",
                    "severity": "high",
                    "case_id": "NETWORK",
                    "step_num": 0,
                    "summary": f"Backend response {status_i} for {item.get('bucket')}",
                    "details": item,
                }
            )
    return findings


DISCOVERY_KEYWORDS = [
    "online",
    "leas",
    "leasing",
    "angebot",
    "weiter",
    "checkout",
    "konfigur",
    "zusammenfassung",
]


def _inventory_top_candidates(inventory: dict, *, limit: int = 12) -> list[dict]:
    if not isinstance(inventory, dict):
        return []
    items = inventory.get("items") or []
    if not isinstance(items, list):
        return []

    def is_clickable(item: dict) -> bool:
        tag = (item.get("tag") or "").lower()
        role = (item.get("role") or "").lower()
        return tag in {"button", "a"} or "button" in role or "link" in role

    clickable = [i for i in items if isinstance(i, dict) and is_clickable(i)]
    return clickable[: max(0, int(limit))]


def _candidate_text(item: dict) -> str:
    parts = [
        str(item.get("text") or ""),
        str(item.get("ariaLabel") or ""),
        str(item.get("testid") or ""),
        str(item.get("href") or ""),
    ]
    return " ".join([p for p in parts if p]).strip()


def _summarize_candidates(inventory: dict, *, limit: int = 6) -> str:
    cands = _inventory_top_candidates(inventory, limit=limit)
    lines = []
    for idx, item in enumerate(cands, start=1):
        css_path = (item.get("cssPath") or "").strip()
        score = item.get("score")
        lines.append(f"{idx}) score={score} css={css_path} text={_candidate_text(item)}")
    return " | ".join(lines)


def _apply_stealth(context) -> None:
    """Best-effort anti-automation fingerprints (lightweight, no external deps)."""
    try:
        context.add_init_script(
            """
            // Hide webdriver
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """
        )
    except Exception:
        pass


def ensure_summary_open(page) -> bool:
    """Ensures the configurator 'Zusammenfassung' section is active.

    The eCom CTA (e.g. 'Online leasen') is typically rendered inside the summary.
    """
    selectors = [
        '[data-testid="stepnavigation-summary"]',
        'button[aria-label="Zusammenfassung"]',
        'button:has-text("Zusammenfassung")',
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.count() == 0:
                continue
            btn = loc.first
            if not btn.is_visible():
                continue
            btn.scroll_into_view_if_needed(timeout=5000)
            btn.click(timeout=10000)
            try:
                page.wait_for_load_state('domcontentloaded', timeout=8000)
            except PlaywrightTimeoutError:
                pass
            page.wait_for_timeout(500)
            return True
        except Exception:
            continue
    return False


def _stabilize_for_evidence(page, *, timeout_ms: int = 15000) -> None:
    """Best-effort stabilization before taking evidence screenshots.

    Goal: avoid capturing blank/loading states and reduce report/screenshot drift.
    """
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
    except Exception:
        pass
    try:
        page.wait_for_function("document.readyState === 'complete'", timeout=min(timeout_ms, 12000))
    except Exception:
        pass
    # Give the browser one more frame for layout/SPA hydration.
    try:
        page.wait_for_timeout(500)
    except Exception:
        pass
    # Best-effort: wait for any meaningful anchor. Don't fail if absent.
    try:
        page.locator(
            '[data-testid="summary-finance-wrapper"], [data-testid="nav-bar"], [data-testid="form-wrapper"], [data-testid="forms-group-container"], [data-testid="cta-next-step"], body'
        ).first.wait_for(state="visible", timeout=min(timeout_ms, 8000))
    except Exception:
        pass


def _resolve_open_url(initial_url: str, value: str | None) -> str | None:
    """Resolve charter 'Open URL' values to absolute URLs.

    Charter often uses paths like '/konfigurator.html/...'. We keep the locale prefix
    from the provided initial URL (e.g. '/de1').
    """
    if not value:
        return None
    v = str(value).strip()
    if not v:
        return None
    if v.lower().startswith("http://") or v.lower().startswith("https://"):
        return v

    try:
        from urllib.parse import urlparse
    except Exception:
        return None

    try:
        p = urlparse(initial_url)
        if not p.scheme or not p.netloc:
            return None
        base = f"{p.scheme}://{p.netloc}"
        # locale segment is the first path component, e.g. '/de1/...'
        parts = [x for x in (p.path or "").split("/") if x]
        locale = parts[0] if parts else ""
        if v.startswith("/"):
            if locale and not v.startswith(f"/{locale}/") and not v.startswith(f"/{locale}?"):
                return f"{base}/{locale}{v}"
            return f"{base}{v}"
        # relative path
        if locale:
            return f"{base}/{locale}/{v.lstrip('/')}"
        return f"{base}/{v.lstrip('/')}"
    except Exception:
        return None


def _try_discovery_click(page, step: dict, inventory: dict, *, max_attempts: int = 6) -> tuple[bool, str, object]:
    """Try to progress the journey by clicking plausible CTA candidates.

    Uses UI inventory (cssPath) and keyword heuristics; considers success when URL changes
    (redacted) or a popup opens.
    """
    before = redact_url_for_logging(getattr(page, "url", "") or "")
    targets = []
    for key in ("text", "name", "aria-label", "aria_label"):
        val = step.get(key)
        if isinstance(val, str) and val.strip():
            targets.append(val.strip().lower())
    keywords = [k for k in DISCOVERY_KEYWORDS]
    # If step provides a target phrase, bias towards it.
    if targets:
        keywords = targets + keywords

    def matches(item: dict) -> bool:
        hay = _candidate_text(item).lower()
        return any(k in hay for k in keywords)

    candidates = [c for c in _inventory_top_candidates(inventory, limit=60) if matches(c)]
    # Fallback: if nothing matches, try the very top clickable ones.
    if not candidates:
        candidates = _inventory_top_candidates(inventory, limit=12)

    attempts = 0
    for item in candidates:
        if attempts >= int(max_attempts):
            break
        css_path = (item.get("cssPath") or "").strip()
        if not css_path:
            continue
        attempts += 1
        try:
            loc = page.locator(css_path).first
            loc.scroll_into_view_if_needed(timeout=5000)
            new_page = None
            try:
                with page.context.expect_page(timeout=2500) as new_page_info:
                    loc.click(timeout=10000, no_wait_after=True)
                new_page = new_page_info.value
            except PlaywrightTimeoutError:
                # No new page opened; click still happened.
                pass

            if new_page:
                page = new_page

            try:
                page.wait_for_load_state('domcontentloaded', timeout=15000)
            except PlaywrightTimeoutError:
                pass

            after = redact_url_for_logging(getattr(page, "url", "") or "")
            if after and after != before:
                return True, f"discovery-click succeeded (url changed): {css_path}", page
            # No URL change — still could be SPA state change; treat as weak success if keyword matched.
            if matches(item):
                return True, f"discovery-click applied (no url change): {css_path}", page
        except Exception:
            continue

    return False, "discovery-click: no viable candidate succeeded", page


def _is_likely_ecom_page(page) -> bool:
    """Heuristic: distinguish eCom journey page from configurator."""
    try:
        url = (getattr(page, "url", "") or "").lower()
        if any(k in url for k in ("checkout", "ecom", "order", "bestellung")):
            return True
    except Exception:
        pass
    try:
        # Configurator summary hook should not exist on eCom page.
        if page.locator('[data-testid="summary-finance-wrapper"]').count() > 0:
            return False
    except Exception:
        pass
    # Content heuristics (German/English)
    needles = [
        "persönliche daten",
        "personal data",
        "next step",
        "nächster schritt",
        "weiter",
    ]
    try:
        content = (page.content() or "").lower()
        return any(n in content for n in needles)
    except Exception:
        return False


def _assert_visible_any(page, selectors: list[str], *, timeout_ms: int = 4000) -> tuple[bool, str]:
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.count() == 0:
                continue
            el = loc.first
            el.wait_for(state="visible", timeout=timeout_ms)
            return True, sel
        except Exception:
            continue
    return False, ""


def _assert_role_button_name_regex(page, pattern: str, *, timeout_ms: int = 4000) -> tuple[bool, str]:
    try:
        rx = re.compile(pattern, re.IGNORECASE)
        loc = page.get_by_role("button", name=rx)
        if loc.count() == 0:
            return False, ""
        loc.first.wait_for(state="visible", timeout=timeout_ms)
        return True, f"role=button name=/{pattern}/i"
    except Exception:
        return False, ""


def ensure_report_exists(report_file: Path, charter_file: Path) -> None:
    """Ensures the HTML report file exists before attempting in-place updates."""
    report_file = Path(report_file)
    charter_file = Path(charter_file)

    if report_file.exists():
        return

    report_file.parent.mkdir(parents=True, exist_ok=True)
    (report_file.parent / "screenshots").mkdir(exist_ok=True)

    generator_script = Path(__file__).resolve().parent / "generate_test_report.py"
    if not generator_script.exists():
        raise FileNotFoundError(f"Report generator not found: {generator_script}")

    if not charter_file.exists():
        raise FileNotFoundError(f"Charter file not found: {charter_file}")

    print(f"--- Report file not found. Generating initial report at: {report_file} ---")
    cmd = [
        sys.executable,
        str(generator_script),
        "--input",
        str(charter_file),
        "--output-dir",
        str(report_file.parent),
        "--title",
        "BTO Test Report",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "Failed to generate initial report.\n"
            f"Command: {' '.join(cmd)}\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

    default_report = report_file.parent / "BTO_Test_Report_v1.0.html"
    if default_report.exists() and default_report.resolve() != report_file.resolve():
        shutil.copyfile(default_report, report_file)

    if not report_file.exists():
        raise FileNotFoundError(
            "Initial report generation did not create the expected report file. "
            f"Expected: {report_file} (or default: {default_report})"
        )

    print(f"--- ✅ Initial report created: {report_file} ---")


def normalize_action(action: str) -> str:
    a = (action or "").strip().lower()
    if a in ("open url", "open", "goto", "navigate"):
        return "open_url"
    if a in ("wait", "sleep"):
        return "wait"
    if a in ("click", "click cta", "tap"):
        return "click"
    if a in ("fill", "fill input", "type", "enter"):
        return "fill"
    if a in ("check", "verify", "verify ui elements", "assert"):
        return "check"
    if a in ("intent", "goal", "agent", "agent step"):
        return "intent"
    return a.replace(" ", "_")


def _within(locator, container_selector: str):
    return locator.page.locator(container_selector).locator(":scope").locator(locator.selector)


def _find_checkout_cta(page):
    """Adaptive locator for the eCom checkout CTA on configurator summary.

    Uses stable product hooks when available and falls back to semantic roles/text.
    """
    container = '[data-testid="summary-finance-wrapper"]'
    candidates = [
        # Most stable: wrapper + shopping cart icon
        f"{container} button:has([data-testid=\"icon-ShoppingCart\"])",
        f"{container} a:has([data-testid=\"icon-ShoppingCart\"])",
        # Wrapper + text
        f"{container} button:has-text(\"Online leasen\")",
        f"{container} a:has-text(\"Online leasen\")",
        # Last resort (semantic)
        "role=button name=Online leasen",
        "role=link name=Online leasen",
    ]
    for sel in candidates:
        try:
            if sel.startswith("role="):
                # Use Playwright's role engine
                if "role=button" in sel:
                    loc = page.get_by_role("button", name="Online leasen")
                else:
                    loc = page.get_by_role("link", name="Online leasen")
            else:
                loc = page.locator(sel)
            if loc.count() == 0:
                continue
            el = loc.first
            if not el.is_visible():
                continue
            return el, sel
        except Exception:
            continue
    return None, ""


def execute_intent(page, step: dict, *, run_dir: Path) -> tuple[object, str, str]:
    """Executes a high-level intent step.

    Returns (status, message).
    """
    intent = (step.get("intent") or step.get("goal") or step.get("name") or "").strip().lower()
    if not intent:
        return page, "Warn", "intent: missing 'intent' field"

    if intent in {"start_checkout", "start_checkout_journey", "start ecom", "start ecom journey"}:
        # Prepare: ensure the summary section is open (CTA is rendered there).
        ensure_summary_open(page)

        before = redact_url_for_logging(getattr(page, "url", "") or "")
        cta, used = _find_checkout_cta(page)
        if not cta:
            # Discovery but constrained: export one inventory and try in-wrapper matches first.
            inv = export_ui_inventory(page, Path(run_dir), prefix="ui_inventory_intent_start_checkout")
            ok, msg, page = _try_discovery_click(page, {"text": "Online leasen"}, inv, max_attempts=6)
            if ok:
                return page, "Warn", f"intent start_checkout: {msg}"
            return page, "Fail", "intent start_checkout: CTA not found (expected under data-testid=summary-finance-wrapper)"

        try:
            cta.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass

        new_page = None
        try:
            with page.context.expect_page(timeout=3000) as new_page_info:
                cta.click(timeout=10000, no_wait_after=True)
            new_page = new_page_info.value
        except PlaywrightTimeoutError:
            # No new page opened; click still happened.
            pass
        except Exception:
            pass

        if new_page:
            page = new_page

        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except PlaywrightTimeoutError:
            pass

        # Best-effort: wait for checkout URL to reduce flakiness.
        try:
            page.wait_for_url("**/checkout.html*", timeout=15000)
        except Exception:
            pass

        # Post-click stabilization on the active page.
        try:
            handle_cookie_banner(page)
        except Exception:
            pass
        try:
            check_for_error_page(page)
        except Exception:
            raise

        try:
            _stabilize_for_evidence(page, timeout_ms=15000)
        except Exception:
            pass

        # Best-effort: wait for a stable checkout anchor to appear.
        try:
            page.locator(
                '[data-testid="nav-bar"], [data-testid="form-wrapper"], [data-testid="mydealer-zero-state-info-button"], [data-testid="forms-group-container"]'
            ).first.wait_for(state="visible", timeout=15000)
        except Exception:
            pass

        after = redact_url_for_logging(getattr(page, "url", "") or "")
        if new_page:
            return page, "Pass", f"intent start_checkout: clicked via {used} (new page opened)"
        if after and after != before:
            return page, "Pass", f"intent start_checkout: clicked via {used} (url changed)"
        # SPA: no url change. If heuristics indicate eCom, treat as Pass.
        if _is_likely_ecom_page(page):
            return page, "Pass", f"intent start_checkout: clicked via {used} (SPA transition, eCom markers found)"
        return page, "Warn", f"intent start_checkout: clicked via {used} (no url change observed)"

    if intent in {"assert_checkout_loaded", "assert_ecom_loaded", "assert ecom loaded"}:
        # Deterministic: checkout.html + at least one stable eCom anchor.
        url_l = (getattr(page, "url", "") or "").lower()
        if "checkout.html" not in url_l and not _is_likely_ecom_page(page):
            inv = export_ui_inventory(page, Path(run_dir), prefix="ui_inventory_intent_assert_checkout_loaded")
            return (
                page,
                "Fail",
                "intent assert_checkout_loaded: not on checkout page / eCom markers missing. " + _summarize_candidates(inv, limit=6),
            )

        ok, used = _assert_visible_any(
            page,
            [
                # Observed stable hooks in inventory
                '[data-testid="nav-bar"]',
                '[data-testid="form-wrapper"]',
                '[data-testid="forms-group-container"]',
                '[data-testid="mydealer-zero-state-info-button"]',
            ],
            timeout_ms=15000,
        )
        if ok:
            return page, "Pass", f"intent assert_checkout_loaded: anchor visible ({used})"

        # Fallback: CTA button label is a reliable anchor.
        ok, used = _assert_role_button_name_regex(page, r"Weiter|Next Step|Nächster Schritt", timeout_ms=5000)
        if ok:
            return page, "Pass", f"intent assert_checkout_loaded: anchor visible ({used})"

        inv = export_ui_inventory(page, Path(run_dir), prefix="ui_inventory_intent_assert_checkout_loaded_anchors")
        return page, "Fail", "intent assert_checkout_loaded: checkout opened but anchors not found. " + _summarize_candidates(inv, limit=6)

    if intent in {"assert_tab_slider_present", "assert_tab_slider", "assert tabs"}:
        ok, used = _assert_visible_any(
            page,
            [
                # Observed stable hooks
                '[data-testid="nav-bar"]',
                '[data-testid="nav-bar-item"]',
                # Fallbacks
                "[role=tablist]",
                "[role=tab]",
                "[id^=navbar-tab-]",
            ],
            timeout_ms=15000,
        )
        if ok:
            return page, "Pass", f"intent assert_tab_slider_present: found ({used})"

        # Variant handling: some checkout variants may not show a tab slider at all.
        # If core checkout anchors are present, downgrade to Warn instead of failing hard.
        ok_checkout, used_checkout = _assert_visible_any(
            page,
            [
                '[data-testid="form-wrapper"]',
                '[data-testid="forms-group-container"]',
                '[data-testid="mydealer-zero-state-info-button"]',
            ],
            timeout_ms=3000,
        )
        if not ok_checkout:
            ok_checkout, used_checkout = _assert_role_button_name_regex(
                page,
                r"Weiter|Next Step|Nächster Schritt|Angebot bearbeiten",
                timeout_ms=3000,
            )

        inv = export_ui_inventory(page, Path(run_dir), prefix="ui_inventory_intent_assert_tab_slider")
        if ok_checkout:
            return (
                page,
                "Warn",
                "intent assert_tab_slider_present: tab slider not confirmed (variant?) but checkout anchors present ("
                + str(used_checkout)
                + "). "
                + _summarize_candidates(inv, limit=6),
            )
        return page, "Fail", "intent assert_tab_slider_present: expected tab slider not found. " + _summarize_candidates(inv, limit=6)

    if intent in {"assert_price_box_present", "assert_price_box", "assert price box"}:
        # Prefer a semantic anchor that sits in/near the price box.
        ok, used = _assert_role_button_name_regex(page, r"Angebot bearbeiten", timeout_ms=5000)
        if ok:
            return page, "Pass", f"intent assert_price_box_present: found ({used})"
        ok, used = _assert_visible_any(
            page,
            [
                "button:has-text(\"Angebot bearbeiten\")",
                "[aria-label=\"Angebot bearbeiten\"]",
            ],
            timeout_ms=5000,
        )
        if ok:
            return page, "Pass", f"intent assert_price_box_present: found ({used})"
        inv = export_ui_inventory(page, Path(run_dir), prefix="ui_inventory_intent_assert_price_box")
        # Keep as Warn because some variants might hide the edit link.
        return page, "Warn", "intent assert_price_box_present: not confirmed (variant?) " + _summarize_candidates(inv, limit=6)

    if intent in {"assert_sticky_bar_present", "assert_sticky_bar", "assert next step cta"}:
        # Deterministic: the Next Step CTA exists.
        # Charter/negative-tests explicitly reference data-testid="cta-next-step".
        ok, used = _assert_visible_any(
            page,
            [
                "[data-testid=\"cta-next-step\"]",
                "button[data-testid=\"cta-next-step\"]",
            ],
            timeout_ms=5000,
        )
        if ok:
            return page, "Pass", f"intent assert_sticky_bar_present: found ({used})"

        ok, used = _assert_role_button_name_regex(
            page,
            r"Weiter|Next Step|Nächster Schritt|Fortfahren|Zum Leasingantrag|Zur Zusammenfassung|Zur Bestellung",
            timeout_ms=5000,
        )
        if ok:
            return page, "Pass", f"intent assert_sticky_bar_present: found ({used})"
        ok, used = _assert_visible_any(
            page,
            [
                "button:has-text(\"Weiter\")",
                "button:has-text(\"Next Step\")",
                "button:has-text(\"Nächster Schritt\")",
                "button:has-text(\"Fortfahren\")",
                "button:has-text(\"Zum Leasingantrag\")",
                "button:has-text(\"Zur Zusammenfassung\")",
                "button:has-text(\"Zur Bestellung\")",
            ],
            timeout_ms=5000,
        )
        if ok:
            return page, "Pass", f"intent assert_sticky_bar_present: found ({used})"
        inv = export_ui_inventory(page, Path(run_dir), prefix="ui_inventory_intent_assert_sticky_bar")
        return page, "Fail", "intent assert_sticky_bar_present: Next Step CTA not found. " + _summarize_candidates(inv, limit=6)

    return page, "Warn", f"intent: unsupported '{intent}'"


def _is_journey_driver_test_case(test_case: dict) -> bool:
    """Heuristic to decide whether we may auto-advance after this testcase.

    Many testcases in the charter are pure assertions and assume the UI stays on the
    same checkout step across multiple cases (their Open URL is often null). Auto-advancing
    after such cases desynchronizes report screenshots from the intended step.
    """
    steps = test_case.get("steps") or []
    if not isinstance(steps, list) or not steps:
        return False

    # If the testcase starts with Open URL = null, it typically assumes stable state.
    first = steps[0] if isinstance(steps[0], dict) else {}
    if normalize_action(first.get("action")) == "open_url" and first.get("value") is None:
        return False

    for s in steps:
        if not isinstance(s, dict):
            continue
        a = normalize_action(s.get("action"))
        if a in {"click", "fill", "check"}:
            return True
        if a == "intent":
            intent = str(s.get("intent") or "").strip().lower()
            if intent in {"start_checkout", "start_checkout_journey", "start ecom", "start ecom journey"}:
                return True
    return False


def redact_url_for_logging(url: str) -> str:
    """Redacts query/fragment from URLs to avoid leaking tokens in logs/results."""
    if not url:
        return ""
    try:
        parts = urlsplit(url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    except Exception:
        # Best-effort fallback: strip query/fragment manually
        return url.split("#", 1)[0].split("?", 1)[0]


def export_ui_inventory(page, output_dir: Path, prefix: str = "ui_inventory") -> dict:
    """Exports a lightweight inventory of visible elements and their ARIA/text hooks."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    js = r"""
(() => {
  const isVisible = (el) => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  };

    const pickText = (el) => {
    const t = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
    return t.length > 120 ? t.slice(0, 117) + '...' : t;
  };

    const cssEscape = (s) => {
        try {
            // Modern browsers
            if (window.CSS && CSS.escape) return CSS.escape(String(s));
        } catch (e) {}
        // Minimal fallback
        return String(s).replace(/[^a-zA-Z0-9_\-]/g, (m) => `\\${m}`);
    };

    const cssPath = (el) => {
        if (!el || el.nodeType !== 1) return '';
        if (el.id) return `#${cssEscape(el.id)}`;
        const parts = [];
        let cur = el;
        let depth = 0;
        while (cur && cur.nodeType === 1 && depth < 8) {
            let part = cur.tagName.toLowerCase();
            const tid = cur.getAttribute('data-testid');
            if (tid && tid.length < 80 && !tid.includes('"') && !tid.includes("'")) {
                part += `[data-testid="${tid}"]`;
            }
            const parent = cur.parentElement;
            if (parent) {
                const siblings = Array.from(parent.children).filter(c => c.tagName === cur.tagName);
                if (siblings.length > 1) {
                    const idx = siblings.indexOf(cur);
                    part += `:nth-of-type(${idx + 1})`;
                }
            }
            parts.unshift(part);
            if (cur.id) break;
            cur = parent;
            depth += 1;
        }
        return parts.join(' > ');
    };

    const KEYWORDS = [
        'leas', 'leasing', 'antrag', 'weiter', 'angebot', 'bearbeiten', 'checkout',
        'online', 'konfigur', 'partner', 'abholung', 'zusammenfassung'
    ];

    const nodes = Array.from(document.querySelectorAll(
        '[data-testid], [aria-label], [role], button, a, input, select, textarea'
    ));

        const scored = [];
  for (const el of nodes) {
    if (!isVisible(el)) continue;
    const tag = el.tagName.toLowerCase();
    const role = el.getAttribute('role') || '';
    const ariaLabel = el.getAttribute('aria-label') || '';
    const testid = el.getAttribute('data-testid') || '';
    const id = el.id || '';
    const nameAttr = el.getAttribute('name') || '';
    const typeAttr = el.getAttribute('type') || '';
    const text = pickText(el);
    const href = (el.getAttribute && el.getAttribute('href')) ? el.getAttribute('href') : '';
    const selector = cssPath(el);
    if (!ariaLabel && !testid && !text && !id) continue;

        let score = 0;
        if (tag === 'button') score += 6;
        if (testid) score += 6;
        if (ariaLabel) score += 5;
        if (role) score += 2;
        if (id) score += 1;
        if (text) {
            const lower = text.toLowerCase();
            for (const k of KEYWORDS) {
                if (lower.includes(k)) score += 3;
            }
        }

        scored.push({
      tag,
      role,
      ariaLabel,
      testid,
      id,
      nameAttr,
      typeAttr,
      text,
            href,
            cssPath: selector,
            score,
        });
  }

    scored.sort((a, b) => b.score - a.score);
    const items = scored.slice(0, 250);

  return {
        url: location.origin + location.pathname,
    title: document.title,
    count: items.length,
    items,
  };
})();
"""

    data = page.evaluate(js)
    # Redact URL in exported evidence
    if isinstance(data, dict) and "url" in data:
        data["url"] = redact_url_for_logging(str(data.get("url") or ""))

    json_path = output_dir / f"{prefix}.json"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        f"# UI Inventory ({prefix})",
        "",
        f"- URL: {data.get('url','')}",
        f"- Title: {data.get('title','')}",
        f"- Visible items captured: {data.get('count',0)}",
        "",
        "## Items (first 250)",
        "",
    ]
    for idx, item in enumerate(data.get("items", []), start=1):
        md_lines.append(
            f"{idx}. tag={item.get('tag','')} role={item.get('role','')} aria-label={item.get('ariaLabel','')} data-testid={item.get('testid','')} id={item.get('id','')} name={item.get('nameAttr','')} text={item.get('text','')} css={item.get('cssPath','')} href={item.get('href','')}"
        )

    md_path = output_dir / f"{prefix}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"  🧾 UI inventory exported: {json_path} and {md_path}")
    return data


def find_element(page, step: dict):
    """Tries to locate a target element using multiple strategies."""
    selector_used = ""

    # Best-effort: search in page and in frames (helps if UI is rendered in iframes).
    contexts = [("page", page)]
    try:
        for fr in page.frames:
            contexts.append(("frame", fr))
    except Exception:
        pass

    def first_or_none(locator):
        try:
            if locator and locator.count() > 0:
                return locator.first
        except Exception:
            return None
        return None

    # MCP/Accessibility snapshot support: sometimes the node is a text leaf.
    node_css = step.get("nodeCssSelector") or step.get("node_css_selector")
    if node_css and isinstance(node_css, str) and node_css.strip():
        raw = node_css.strip()
        # MCP sometimes appends '#text' for text nodes; strip it.
        cleaned = raw[:-5] if raw.endswith("#text") else raw
        cleaned = cleaned.rstrip("#").strip()
        if cleaned:
            for _, ctx in contexts:
                try:
                    loc = ctx.locator(cleaned)
                    el = first_or_none(loc)
                    if el:
                        # If we located a non-clickable leaf, climb to nearest button/a.
                        try:
                            clickable = el.locator(
                                "xpath=ancestor-or-self::*[self::button or self::a][1]"
                            ).first
                            if clickable:
                                return clickable, f"mcp:{cleaned}"
                        except Exception:
                            pass
                        return el, f"mcp:{cleaned}"
                except Exception:
                    continue

    selector = step.get("selector")
    if selector:
        for _, ctx in contexts:
            locator = ctx.locator(selector)
            el = first_or_none(locator)
            if el:
                return el, selector

    testid = step.get("data-testid")
    if testid and str(testid).strip() and str(testid) != "placeholder-testid":
        selector_used = f'[data-testid="{testid}"]'
        for _, ctx in contexts:
            locator = ctx.locator(selector_used)
            el = first_or_none(locator)
            if el:
                return el, selector_used

    aria_label = step.get("aria-label") or step.get("aria_label")
    if aria_label:
        aria_label = str(aria_label).strip()
        if aria_label:
            # Prefer exact match, then case-insensitive contains
            exact_sel = f'[aria-label="{aria_label}"]'
            for _, ctx in contexts:
                locator = ctx.locator(exact_sel)
                el = first_or_none(locator)
                if el:
                    return el, exact_sel
            contains_sel = f'[aria-label*="{aria_label}" i]'
            for _, ctx in contexts:
                locator = ctx.locator(contains_sel)
                el = first_or_none(locator)
                if el:
                    return el, contains_sel

    role = step.get("role")
    name = step.get("name")
    if role and name:
        for _, ctx in contexts:
            locator = ctx.get_by_role(str(role), name=str(name))
            el = first_or_none(locator)
            if el:
                return el, f"role={role} name={name}"

    text = step.get("text")
    if text:
        t = str(text)
        # Prefer clicking semantic controls over raw text nodes (often spans).
        for _, ctx in contexts:
            locator = ctx.get_by_role("link", name=t)
            el = first_or_none(locator)
            if el:
                return el, f"role=link name={t}"
        for _, ctx in contexts:
            locator = ctx.get_by_role("button", name=t)
            el = first_or_none(locator)
            if el:
                return el, f"role=button name={t}"
        for _, ctx in contexts:
            locator = ctx.get_by_text(t, exact=True)
            el = first_or_none(locator)
            if el:
                return el, f"text={t}"
        for _, ctx in contexts:
            locator = ctx.get_by_text(t, exact=False)
            el = first_or_none(locator)
            if el:
                return el, f"text~={t}"

    # Backward-compatible fallback: sometimes value is used as label/text
    value = step.get("value")
    if value and isinstance(value, str) and value.strip():
        v = value.strip()
        exact_sel = f'[aria-label="{v}"]'
        for _, ctx in contexts:
            locator = ctx.locator(exact_sel)
            el = first_or_none(locator)
            if el:
                return el, exact_sel
        contains_sel = f'[aria-label*="{v}" i]'
        for _, ctx in contexts:
            locator = ctx.locator(contains_sel)
            el = first_or_none(locator)
            if el:
                return el, contains_sel
        for _, ctx in contexts:
            locator = ctx.get_by_text(v, exact=True)
            el = first_or_none(locator)
            if el:
                return el, f"text={v}"
        for _, ctx in contexts:
            locator = ctx.get_by_text(v, exact=False)
            el = first_or_none(locator)
            if el:
                return el, f"text~={v}"

    return None, selector_used


def _try_auto_repair_click(page, step: dict, inventory: dict) -> tuple[bool, str]:
    """Best-effort: try to click a candidate from the exported UI inventory.

    Returns (success, message).
    """
    if not isinstance(inventory, dict):
        return False, "no inventory data"
    items = inventory.get("items") or []
    if not isinstance(items, list) or not items:
        return False, "empty inventory"

    targets = []
    for key in ("text", "name", "aria-label", "aria_label"):
        val = step.get(key)
        if isinstance(val, str) and val.strip():
            targets.append(val.strip().lower())
    targets = [t for t in targets if t]
    if not targets:
        return False, "no target text/name"

    def is_clickable(item: dict) -> bool:
        tag = (item.get("tag") or "").lower()
        role = (item.get("role") or "").lower()
        return tag in {"button", "a"} or "button" in role or "link" in role

    for item in items:
        if not isinstance(item, dict):
            continue
        if not is_clickable(item):
            continue
        css_path = item.get("cssPath") or ""
        if not isinstance(css_path, str) or not css_path.strip():
            continue
        hay = " ".join(
            [
                str(item.get("text") or ""),
                str(item.get("ariaLabel") or ""),
                str(item.get("testid") or ""),
            ]
        ).lower()
        if not any(t in hay for t in targets):
            continue
        try:
            loc = page.locator(css_path).first
            loc.scroll_into_view_if_needed(timeout=5000)
            loc.click(timeout=10000)
            return True, f"auto-repaired click via cssPath='{css_path}'"
        except Exception:
            continue

    return False, "no matching clickable candidate in inventory"

def update_report(report_path, step_id, status, screenshot_path=None, message=None):
    """Updates the HTML report with the status of a test step."""
    try:
        # It's inefficient to read/write the whole file every time, but simplest for now.
        with report_path.open('r+', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
            badge_id = f"badge-{step_id}"
            badge = soup.find('span', id=badge_id)
            message_id = f"message-{step_id}"
            message_p = soup.find('p', id=message_id)

            if badge:
                badge.string = status
                badge['class'] = ['status-badge', f'status-{status.lower()}']
                print(f"    ✅ Updated badge '{badge_id}' to '{status}'")

                # Update optional message
                if message and message_p:
                    message_p.string = f"Info: {message}"
                    print(f"    ✅ Added message to '{message_id}': {message}")

                # Update screenshot if one was taken
                if screenshot_path:
                    # The screenshot img tag is within the same <details> block as the summary
                    details_tag = badge.find_parent('details')
                    if details_tag:
                        img_tag = details_tag.find('img')
                        if img_tag:
                            # Making the path relative to the report
                            screenshot_as_path = Path(screenshot_path)
                            relative_screenshot_path = Path('screenshots') / screenshot_as_path.name
                            img_tag['src'] = str(relative_screenshot_path).replace('\\', '/')
                            print(f"    ✅ Updated screenshot for '{badge_id}' to '{relative_screenshot_path}'")
                        else:
                            print(f"    ⚠️ Could not find img tag for step {step_id}")
                    else:
                        print(f"    ⚠️ Could not find parent <details> for badge {badge_id}")
                
                f.seek(0)
                f.write(str(soup.prettify()))
                f.truncate()
            else:
                print(f"    ❌ Error: Could not find status badge with ID: {badge_id} in the report.")

    except Exception as e:
        print(f"    ❌ Critical Error updating report: {e}")

def handle_cookie_banner(page):
    """Detects and accepts common cookie consent banners."""
    print("  🔎 Checking for cookie banners...")
    # A list of potential selectors for the "accept all" button
    # Prioritized by reliability (aria-label, role, then text)
    accept_selectors = [
        '#customButton',
        '#ensNotifyBanner #customButton',
        'button#customButton',
        'button:has-text("Zustimmen und weiter")',
        '[aria-label*="Alle akzeptieren" i]',
        '[aria-label*="Accept all" i]',
        'button:has-text("Alle akzeptieren")',
        'button:has-text("Accept All")',
        '#uc-btn-accept-all',
    ]
    
    try:
        for i, selector in enumerate(accept_selectors):
            print(f"    Attempting selector {i+1}/{len(accept_selectors)}: '{selector}'")
            locator = page.locator(selector)
            if locator.count() == 0:
                continue
            button = locator.first
            if button.is_visible():
                print(f"    ✅ Found cookie banner button with selector: '{selector}'. Clicking it.")
                button.click(timeout=5000)
                # Wait for the banner to disappear (if present)
                banner = page.locator('#ensNotifyBanner')
                if banner.count() > 0:
                    try:
                        banner.wait_for(state='hidden', timeout=10000)
                    except PlaywrightTimeoutError:
                        page.wait_for_timeout(1000)
                else:
                    page.wait_for_timeout(1000)
                print("    ✅ Cookie banner handled.")
                return True
        print("  ✅ No common cookie banner found.")
        return False
    except PlaywrightTimeoutError:
        # This is not an error, it just means the selector wasn't found
        print(f"    Selector '{selector}' not found or not visible within timeout.")
        return False
    except Exception as e:
        print(f"  ⚠️ An unexpected error occurred while handling cookie banner: {e}")
        return False

def check_for_error_page(page):
    """Checks if the current page is a known error page (e.g., 401, 404)."""
    print("  🔎 Checking for error pages (401, 404, etc.)...")
    try:
        page_title = page.title().lower()
        page_content = page.content().lower()

        # Be strict to avoid false positives (many apps contain the word "error" in JS/CSS).
        error_checks = [
            ("401 Unauthorized", ["401 unauthorized", "http status 401", "unauthorized"]),
            ("403 Forbidden", ["403 forbidden", "http status 403", "forbidden"]),
            ("404 Not Found", ["404 not found", "http status 404"]),
        ]

        for error_type, needles in error_checks:
            for needle in needles:
                if needle in page_title or needle in page_content:
                    error_message = f"Critical Error: Detected '{error_type}' page. Aborting test."
                    print(f"    ❌ {error_message}")
                    raise Exception(error_message)
        
        print("  ✅ No critical error pages detected.")
        return True
    except Exception as e:
        # Re-raise the exception to stop the test
        raise e


def get_credentials_for_url(url, creds_data):
    """Finds the appropriate credentials for a given URL from the credentials data."""
    for key, cred_object in creds_data.items():
        if isinstance(cred_object, dict) and 'base_url' in cred_object:
            if url.startswith(cred_object['base_url']):
                print(f"  ✅ Found matching credentials for '{redact_url_for_logging(url)}' under key '{key}'.")
                if 'username' in cred_object and 'password' in cred_object:
                    return {
                        'username': cred_object['username'],
                        'password': cred_object['password']
                    }
    print(f"  ⚠️ No matching credentials found for base URL of '{redact_url_for_logging(url)}'.")
    return None

def run_smoketest(
    url,
    charter_file,
    report_file,
    screenshots_dir,
    max_steps=None,
    *,
    stop_on_blocker: bool = True,
    inventory_max: int = 3,
    inventory_on_placeholder: bool = False,
    auto_repair_click: bool = True,
    discovery_click: bool = True,
    headed: bool = False,
    slowmo_ms: int = 0,
    stealth: bool = True,
    pause_for_login: bool = False,
    pause_for_login_seconds: int = 180,
    verify_login: bool = True,
    verify_login_timeout_seconds: int = 20,
    auto_advance: bool = False,
    auto_fill: bool = False,
):
    started_at = _dt.datetime.now().isoformat(timespec="seconds")
    findings: list[dict] = []
    totals = {"steps_total": 0, "pass": 0, "warn": 0, "fail": 0, "aborted": False, "abort_reason": ""}
    inventory_exports = 0

    run_dir = Path(report_file).parent
    net_trace_path = run_dir / "network_trace.jsonl"
    current_step_id_for_net: str | None = None

    api_dir = run_dir / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    page = None
    api_counters: dict[str, int] = {}
    form_definition_schema: dict | None = None

    def _api_write_json(kind: str, payload_obj: object) -> str | None:
        try:
            api_counters[kind] = int(api_counters.get(kind, 0)) + 1
            idx = api_counters[kind]
            path = api_dir / f"{kind}_{idx:03d}.json"
            path.write_text(
                json.dumps(_redact_payload(payload_obj), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return str(Path("api") / path.name)
        except Exception:
            return None

    def maybe_export_inventory(prefix: str) -> dict | None:
        nonlocal inventory_exports
        if inventory_max is not None and inventory_exports >= int(inventory_max):
            return None
        try:
            data = export_ui_inventory(page, Path(report_file).parent, prefix=prefix)
            inventory_exports += 1
            return data
        except Exception:
            return None
    
    # Robustly find and load credentials if they exist
    credentials_path = Path(__file__).resolve().parent.parent / '.secrets' / 'credentials.json'
    http_creds = None
    if credentials_path.exists():
        print("Found credentials file. Attempting to load credentials based on URL.")
        with open(credentials_path, 'r') as f:
            try:
                all_creds = json.load(f)
                http_creds = get_credentials_for_url(url, all_creds)
                if http_creds:
                    print("Successfully loaded basic auth credentials for the target URL.")
                else:
                    print("Could not find matching credentials for the URL. Proceeding without authentication.")
            except json.JSONDecodeError:
                print("Warning: Could not decode credentials.json. Proceeding without authentication.")
    else:
        print("No credentials file found. Proceeding without authentication.")

    with sync_playwright() as p:
        launch_args = ["--disable-blink-features=AutomationControlled"]
        browser = p.chromium.launch(headless=not headed, slow_mo=slowmo_ms or 0, args=launch_args)
        context = browser.new_context(http_credentials=http_creds)
        if stealth:
            _apply_stealth(context)

        # --- Network capture (safe, targeted) ---
        # Goal: replicate MCP/DevTools insight (requests/responses) as local artefacts.
        def _net_mark(event: str, extra: dict | None = None) -> None:
            rec = {
                "ts": _dt.datetime.now().isoformat(timespec="milliseconds"),
                "event": event,
                "step": current_step_id_for_net,
            }
            if extra:
                rec.update(extra)
            _append_jsonl(net_trace_path, rec)

        def _is_target_url(u: str) -> bool:
            ul = (u or "").lower()
            return ("processopportunities" in ul) or ("duc-leasing" in ul)

        def _is_backendish_url(u: str) -> bool:
            # Log lightweight metadata for backend-ish calls so the trace is useful
            # even when the run does not reach the final submit step.
            raw = (u or "")
            ul = raw.lower()

            # Avoid noisy analytics/telemetry endpoints.
            try:
                host = urlsplit(raw).netloc.lower()
            except Exception:
                host = ""
            deny_hosts = (
                "fsignals.plt-live.net",
                "google-analytics",
                "googletagmanager",
                "doubleclick",
                "hotjar",
                "sentry",
                "datadoghq",
            )
            if host and any(d in host for d in deny_hosts):
                return False

            # Allowlist of relevant product/backend endpoints.
            return (
                ("/bff-forms/" in ul)
                or ("/bff/" in ul)
                or ("/app/authproxy/" in ul)
                or ("processopportunities" in ul)
                or ("duc-leasing" in ul)
                or ("chosenvehicle" in ul)
                or ("chosen-vehicle" in ul)
                or ("pickuplocation" in ul)
                or ("pickup-location" in ul)
                or ("/pickup" in ul)
                or ("webcalc" in ul)
                or ("sds" in ul)
                or ("dealer" in ul)
            )

        def _category_for_url(u: str) -> str | None:
            ul = (u or "").lower()
            if "processopportunities" in ul:
                return "processOpportunities"
            if "duc-leasing" in ul:
                return "duc_leasing"
            if "pickuplocation" in ul or "pickup-location" in ul:
                return "pickupLocation"
            if "/pickup" in ul:
                return "pickup"
            if "chosenvehicle" in ul or "chosen-vehicle" in ul:
                return "chosenVehicle"
            if "sds" in ul or "dealer" in ul:
                return "dealer"
            return None

        def _safe_url(u: str) -> str:
            return redact_url_for_logging(u or "")

        def _snapshot_form_inputs() -> dict | None:
            """Best-effort: snapshot of current form inputs without persisting PII.

            Captures visible inputs/selects and stores only sha256+len for values.
            No plaintext values are written to disk.
            """
            nonlocal page
            if not page:
                return None

            js = r"""
(() => {
    const isVisible = (el) => {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
    };

    const pickLabel = (el) => {
        try {
            if (el.labels && el.labels.length) {
                const t = (el.labels[0].innerText || el.labels[0].textContent || '').trim();
                return t.replace(/\s+/g, ' ').slice(0, 120);
            }
        } catch (e) {}
        return (el.getAttribute('aria-label') || el.getAttribute('name') || el.id || '').trim().slice(0, 120);
    };

    const nodes = Array.from(document.querySelectorAll('input, textarea, select'));
    const items = [];
    for (const el of nodes) {
        if (!isVisible(el)) continue;
        const tag = el.tagName.toLowerCase();
        const type = (el.getAttribute('type') || '').toLowerCase();
        const testid = el.getAttribute('data-testid') || '';
        const name = el.getAttribute('name') || '';
        const id = el.id || '';
        let value = '';
        let checked = null;
        try {
            if (tag === 'select') {
                value = el.value || '';
            } else if (type === 'checkbox' || type === 'radio') {
                checked = !!el.checked;
                value = el.value || '';
            } else {
                value = el.value || '';
            }
        } catch (e) {}
        items.push({ tag, type, label: pickLabel(el), testid, name, id, value, checked });
        if (items.length >= 200) break;
    }
    return { url: location.origin + location.pathname, count: items.length, items };
})();
"""

            try:
                data = page.evaluate(js)
            except Exception:
                return None

            if not isinstance(data, dict):
                return None

            items = data.get("items") or []
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    raw_value = item.pop("value", "")
                    if raw_value is None:
                        raw_value = ""
                    raw_value = str(raw_value)
                    item["value"] = {"_sha256": _sha256_str(raw_value), "_len": len(raw_value)}

            data["url"] = redact_url_for_logging(str(data.get("url") or ""))
            return data

        def on_request(request) -> None:
            try:
                if not (_is_target_url(request.url) or _is_backendish_url(request.url)):
                    return
                rec = {
                    "type": "request",
                    "method": request.method,
                    "resourceType": request.resource_type,
                    "url": _safe_url(request.url),
                }

                # Keep headers only for the two primary targets (risk-reduced).
                if _is_target_url(request.url):
                    rec["headers"] = _net_headers_redacted(request.headers)

                # Persist processOpportunities request payload (redacted)
                if "processopportunities" in (request.url or "").lower() and (request.method or "").upper() == "POST":
                    post = request.post_data or ""
                    payload_obj = None
                    try:
                        payload_obj = json.loads(post) if post else None
                    except Exception:
                        payload_obj = None

                    if payload_obj is not None:
                        red = _redact_payload(payload_obj)
                        (run_dir / "processOpportunities_payload_redacted.json").write_text(
                            json.dumps(red, ensure_ascii=False, indent=2),
                            encoding="utf-8",
                        )
                        saved_api = _api_write_json("processOpportunities_payload", payload_obj)
                        if saved_api:
                            rec["saved_api"] = saved_api
                        rec["saved"] = "processOpportunities_payload_redacted.json"

                        snap = _snapshot_form_inputs()
                        if snap is not None:
                            (run_dir / "form_snapshot_before_processOpportunities.json").write_text(
                                json.dumps(snap, ensure_ascii=False, indent=2),
                                encoding="utf-8",
                            )
                            rec["form_snapshot"] = "form_snapshot_before_processOpportunities.json"
                    else:
                        rec["note"] = "processOpportunities POST payload was not JSON"

                if "duc-leasing" in (request.url or "").lower() and (request.method or "").upper() == "POST":
                    post = request.post_data or ""
                    payload_obj = None
                    try:
                        payload_obj = json.loads(post) if post else None
                    except Exception:
                        payload_obj = None
                    if payload_obj is not None:
                        red = _redact_payload(payload_obj)
                        (run_dir / "duc_leasing_request_redacted.json").write_text(
                            json.dumps(red, ensure_ascii=False, indent=2),
                            encoding="utf-8",
                        )
                        saved_api = _api_write_json("duc_leasing_request", payload_obj)
                        if saved_api:
                            rec["saved_api"] = saved_api
                        rec["saved"] = "duc_leasing_request_redacted.json"

                        snap = _snapshot_form_inputs()
                        if snap is not None:
                            (run_dir / "form_snapshot_before_duc_leasing.json").write_text(
                                json.dumps(snap, ensure_ascii=False, indent=2),
                                encoding="utf-8",
                            )
                            rec["form_snapshot"] = "form_snapshot_before_duc_leasing.json"

                _append_jsonl(net_trace_path, {"ts": _dt.datetime.now().isoformat(timespec="milliseconds"), "step": current_step_id_for_net, **rec})
            except Exception:
                pass

        def on_response(response) -> None:
            try:
                req = response.request
                if not (_is_target_url(req.url) or _is_backendish_url(req.url)):
                    return

                rec = {
                    "type": "response",
                    "status": response.status,
                    "ok": response.ok,
                    "url": _safe_url(req.url),
                    "resourceType": req.resource_type,
                }

                ul = (req.url or "").lower()

                # Persist formDefinition (redacted) so we can learn patterns/required fields.
                # This payload can contain sensitive targetUrl query params (x-api-key), so we
                # always run it through _redact_payload before writing.
                nonlocal form_definition_schema
                if "/bff-forms/formdefinition" in ul:
                    try:
                        body = response.json()
                    except Exception:
                        body = None
                    if isinstance(body, dict):
                        safe_body = _redact_payload(body)
                        try:
                            (run_dir / "formDefinition_response_redacted.json").write_text(
                                json.dumps(safe_body, ensure_ascii=False, indent=2),
                                encoding="utf-8",
                            )
                            rec["saved"] = "formDefinition_response_redacted.json"
                        except Exception:
                            pass
                        saved_api = _api_write_json("formDefinition_response", safe_body)
                        if saved_api:
                            rec["saved_api"] = saved_api
                        form_definition_schema = safe_body

                category = _category_for_url(req.url)
                if category and category not in {"processOpportunities", "duc_leasing"}:
                    try:
                        body = response.json()
                    except Exception:
                        body = None
                    if body is not None:
                        saved_api = _api_write_json(f"{category}_response", body)
                        if saved_api:
                            rec["saved_api"] = saved_api
                if "duc-leasing" in ul:
                    try:
                        body = response.json()
                    except Exception:
                        body = None
                    if body is not None:
                        red = _redact_payload(body)
                        (run_dir / "duc_leasing_response.json").write_text(
                            json.dumps(red, ensure_ascii=False, indent=2),
                            encoding="utf-8",
                        )
                        saved_api = _api_write_json("duc_leasing_response", body)
                        if saved_api:
                            rec["saved_api"] = saved_api
                        rec["saved"] = "duc_leasing_response.json"

                if "processopportunities" in ul:
                    try:
                        body = response.json()
                    except Exception:
                        body = None
                    if body is not None:
                        red = _redact_payload(body)
                        (run_dir / "processOpportunities_response_redacted.json").write_text(
                            json.dumps(red, ensure_ascii=False, indent=2),
                            encoding="utf-8",
                        )
                        saved_api = _api_write_json("processOpportunities_response", body)
                        if saved_api:
                            rec["saved_api"] = saved_api
                        rec["saved_response"] = "processOpportunities_response_redacted.json"

                _append_jsonl(net_trace_path, {"ts": _dt.datetime.now().isoformat(timespec="milliseconds"), "step": current_step_id_for_net, **rec})
            except Exception:
                pass

        context.on("request", on_request)
        context.on("response", on_response)
        _net_mark("network_capture_enabled", {"targets": ["processOpportunities", "duc-leasing"], "file": str(net_trace_path.name)})

        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        os.makedirs(screenshots_dir, exist_ok=True)

        # Ensure report exists before the first update_report() call
        ensure_report_exists(report_file, charter_file)

        with open(charter_file, 'r') as f:
            test_scenarios = json.load(f)

        def _collect_ui_alerts(page) -> dict | None:
            """Collect visible validation/alert messages (no PII) for evidence."""
            js = r"""
(() => {
  const isVisible = (el) => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  };

  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();

  const selectors = [
    '[role="alert"]',
    '[aria-live="assertive"]',
    '[aria-live="polite"]',
    '[aria-invalid="true"]',
    '.error',
    '.errors',
    '.invalid',
    '.form-error',
    '.helper-text',
  ];

  const nodes = [];
  for (const sel of selectors) {
    try {
      for (const el of Array.from(document.querySelectorAll(sel))) nodes.push(el);
    } catch (e) {}
  }

  const items = [];
  for (const el of nodes) {
    if (!isVisible(el)) continue;
    const txt = norm(el.innerText || el.textContent || '');
    if (!txt) continue;
    // Keep it short and non-sensitive.
    items.push(txt.slice(0, 240));
    if (items.length >= 15) break;
  }

  return { count: items.length, items };
})();
"""
            try:
                data = page.evaluate(js)
            except Exception:
                return None
            if not isinstance(data, dict):
                return None
            return data

        def _extract_form_field_hints(schema: dict | None) -> dict:
            """Flatten formDefinition to cid->field metadata (best-effort)."""
            if not isinstance(schema, dict):
                return {}

            root = schema.get("formDefinition") if "formDefinition" in schema else schema
            if not isinstance(root, dict):
                return {}

            out: dict[str, dict] = {}

            def walk(node: object) -> None:
                if isinstance(node, dict):
                    cid = node.get("cid")
                    if isinstance(cid, str) and cid.strip():
                        out[cid.strip().lower()] = {
                            "cid": cid,
                            "type": node.get("type"),
                            "label": node.get("label"),
                            "required": bool(node.get("required")) if "required" in node else None,
                            "pattern": node.get("pattern"),
                            "inputType": node.get("inputType"),
                            "options": node.get("options") if isinstance(node.get("options"), list) else None,
                        }
                    for k, v in node.items():
                        if k == "options":
                            continue
                        walk(v)
                elif isinstance(node, list):
                    for it in node:
                        walk(it)

            walk(root.get("fields"))
            return out

        def _auto_fill_common_fields(page) -> tuple[bool, str]:
            """Best-effort fill for common personal-data fields.

            Uses only non-sensitive dummy values. Goal is to enable 'Next Step' CTA
            so that the journey can actually progress in automated runs.
            """
            js = r"""
(() => {
  const isVisible = (el) => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  };

  const pickLabel = (el) => {
    try {
      if (el.labels && el.labels.length) {
        const t = (el.labels[0].innerText || el.labels[0].textContent || '').trim();
        return t.replace(/\s+/g, ' ').slice(0, 120);
      }
    } catch (e) {}
    return (el.getAttribute('aria-label') || el.getAttribute('name') || el.id || '').trim().slice(0, 120);
  };

    const pickHint = (el) => {
        const parts = [
            pickLabel(el),
            (el.getAttribute('placeholder') || '').trim(),
            (el.getAttribute('autocomplete') || '').trim(),
            (el.getAttribute('name') || '').trim(),
            (el.id || '').trim(),
            (el.getAttribute('data-testid') || '').trim(),
            (el.getAttribute('type') || '').trim(),
        ].filter(Boolean);
        return parts.join(' | ').replace(/\s+/g, ' ').slice(0, 240);
    };

    const nodes = Array.from(document.querySelectorAll('input, textarea, select'));
    const items = [];
    for (const el of nodes) {
    if (!isVisible(el)) continue;
    const tag = el.tagName.toLowerCase();
        const type = (el.getAttribute('type') || '').toLowerCase();
        const role = (el.getAttribute('role') || '').toLowerCase();
        if (tag === 'input' && (type === 'hidden' || type === 'password')) continue;
    const patternAttr = (el.getAttribute('pattern') || '').trim();
    const required = (() => { try { return !!el.required; } catch (e) { return null; } })();
    const minLength = (() => { try { return typeof el.minLength === 'number' ? el.minLength : null; } catch (e) { return null; } })();
    const maxLength = (() => { try { return typeof el.maxLength === 'number' ? el.maxLength : null; } catch (e) { return null; } })();
    const testid = el.getAttribute('data-testid') || '';
    const name = el.getAttribute('name') || '';
    const id = el.id || '';
        const placeholder = (el.getAttribute('placeholder') || '').trim();
        const autocomplete = (el.getAttribute('autocomplete') || '').trim();
    let value = '';
    try { value = el.value || ''; } catch (e) {}
        let checked = null;
        try {
            if (tag === 'input' && type === 'checkbox') checked = !!el.checked;
        } catch (e) {}
    let selector = '';
    if (testid) selector = `[data-testid="${testid.replace(/"/g,'\\"')}"]`;
    else if (id) selector = `#${CSS.escape(id)}`;
    else if (name) selector = `[name="${name.replace(/"/g,'\\"')}"]`;

        let options = null;
        if (tag === 'select') {
            try {
                options = Array.from(el.options || []).slice(0, 25).map(o => ({
                    value: (o.value || '').trim(),
                    label: (o.label || o.textContent || '').trim().replace(/\s+/g,' ').slice(0, 120),
                    disabled: !!o.disabled,
                }));
            } catch (e) {
                options = null;
            }
        }

        items.push({
            tag, type, role,
            label: pickLabel(el),
            hint: pickHint(el),
            placeholder, autocomplete,
            testid, name, id, selector,
            value, checked,
            patternAttr, required, minLength, maxLength,
            options,
        });
    if (items.length >= 100) break;
  }
  return { count: items.length, items };
})();
"""

            try:
                data = page.evaluate(js)
            except Exception:
                return False, "auto-fill: page.evaluate failed"
            if not isinstance(data, dict):
                return False, "auto-fill: unexpected data"
            items = data.get("items") or []
            if not isinstance(items, list) or not items:
                return False, "auto-fill: no visible inputs"

            filled = 0
            attempted = 0

            schema_hints = _extract_form_field_hints(form_definition_schema)

            def _norm_hint(s: str) -> str:
                return (s or "").strip().lower()

            def _looks_digits_pattern(p: str) -> bool:
                pl = (p or "").lower()
                return ("[0-9]" in pl or "\\d" in pl) and ("{" in pl and "}" in pl)

            def _value_for_schema(cid_key: str) -> str | None:
                spec = schema_hints.get(cid_key)
                if not isinstance(spec, dict):
                    return None
                label = str(spec.get("label") or "").lower()
                pat = str(spec.get("pattern") or "")
                itype = str(spec.get("inputType") or "").lower()
                ftype = str(spec.get("type") or "").lower()

                if ftype == "select":
                    opts = spec.get("options")
                    if isinstance(opts, list) and opts:
                        # Prefer plausible defaults.
                        for o in opts:
                            if not isinstance(o, dict):
                                continue
                            val = str(o.get("value") or "").strip()
                            if not val:
                                continue
                            if cid_key in {"mobilephonecountrycode"} and val == "+49":
                                return val
                            if cid_key in {"salutation"} and val in {"MR", "MS"}:
                                return val
                            if cid_key in {"title"} and val:
                                return val
                        # Else first non-empty option.
                        for o in opts:
                            if not isinstance(o, dict):
                                continue
                            val = str(o.get("value") or "").strip()
                            if val:
                                return val
                    return None

                if "email" in cid_key or "e-mail" in label or itype == "email":
                    return "john.doe@example.com"
                if "mobilephonenumber" in cid_key or "mobil" in label or "phone" in label:
                    # Pattern requires digits only (no + or spaces) in this form.
                    return "15112345678"
                if cid_key in {"zip", "postalcode", "postcode"} or "postleitz" in label:
                    return "12345"
                if cid_key in {"street"} or "straße" in label or "strasse" in label:
                    # Street field disallows digits; houseNumber is separate.
                    return "Teststraße"
                if cid_key in {"housenumber", "house_number"} or "hausnummer" in label:
                    return "1"
                if cid_key in {"city", "ort"} or "stadt" in label:
                    return "Berlin"
                if cid_key in {"firstname", "first_name"} or "vorname" in label:
                    return "John"
                if cid_key in {"lastname", "last_name"} or "nachname" in label:
                    return "Doe"
                # Generic fallback based on pattern.
                if pat and _looks_digits_pattern(pat):
                    return "12345"
                return None

            def pick_value(*, hint: str, tag: str, input_type: str, autocomplete: str, pattern_attr: str) -> str | None:
                h = (hint or "").strip().lower()
                it = (input_type or "").strip().lower()
                ac = (autocomplete or "").strip().lower()
                pat = (pattern_attr or "").strip()

                # Prefer schema-derived values when we can infer cid from hint.
                for cid_key in (
                    "firstname",
                    "lastname",
                    "email",
                    "mobilephonecountrycode",
                    "mobilephonenumber",
                    "street",
                    "housenumber",
                    "zip",
                    "city",
                    "salutation",
                    "title",
                ):
                    if cid_key in h:
                        v = _value_for_schema(cid_key)
                        if v:
                            return v

                # DOM pattern hints (works even without schema capture)
                if pat:
                    pl = pat.lower()
                    if "[0-9]{5}" in pl or "\\d{5}" in pl:
                        return "12345"
                    if "[0-9]{5,15}" in pl or "\\d{5,15}" in pl:
                        return "15112345678"
                    # Street pattern in this form forbids digits
                    if "äöü" in pl and "0-9" not in pl and any(k in h for k in ["straße", "strasse", "street"]):
                        return "Teststraße"

                if tag == "input" and it == "email":
                    return "john.doe@example.com"

                if ac in {"given-name", "given_name", "firstname", "first_name"}:
                    return "John"
                if ac in {"family-name", "family_name", "lastname", "last_name"}:
                    return "Doe"
                if ac == "email":
                    return "john.doe@example.com"
                if ac in {"tel", "tel-national", "tel-local", "mobile"}:
                    # Digits-only to satisfy patterns like ^[0-9]{5,15}$
                    return "15112345678"
                if ac in {"postal-code", "postal_code", "zip"}:
                    return "12345"
                if ac in {"street-address", "street_address"}:
                    return "Teststraße"

                if any(k in h for k in ["vorname", "firstname", "first name", "given name", "given-name", "first_name"]):
                    return "John"
                if any(k in h for k in ["nachname", "lastname", "last name", "surname", "family name", "family-name", "last_name"]):
                    return "Doe"
                if any(k in h for k in ["e-mail", "email", "mail", "e_mail"]):
                    return "john.doe@example.com"
                if any(k in h for k in ["telefon", "phone", "mobile", "handy", "tel"]):
                    return "15112345678"
                if any(k in h for k in ["plz", "postleitz", "postal", "zip"]):
                    return "12345"
                if any(k in h for k in ["hausnummer", "house number", "housenumber"]):
                    return "1"
                if any(k in h for k in ["straße", "strasse", "street", "address"]):
                    return "Teststraße"
                if any(k in h for k in ["stadt", "ort", "city"]):
                    return "Berlin"
                return None

            def is_consent_checkbox(*, hint: str) -> bool:
                h = (hint or "").strip().lower()
                keywords = [
                    "agb",
                    "datenschutz",
                    "privacy",
                    "terms",
                    "bedingungen",
                    "einverstanden",
                    "zustimm",
                    "consent",
                    "agree",
                    "accept",
                ]
                return any(k in h for k in keywords)

            for it in items:
                if not isinstance(it, dict):
                    continue
                selector = str(it.get("selector") or "").strip()
                tag = str(it.get("tag") or "")
                input_type = str(it.get("type") or "")
                autocomplete = str(it.get("autocomplete") or "")
                hint = str(it.get("hint") or it.get("label") or "")
                value = str(it.get("value") or "")
                pattern_attr = str(it.get("patternAttr") or "")
                if not selector:
                    continue

                # Consent checkbox
                if tag == "input" and input_type.lower() == "checkbox":
                    try:
                        checked = bool(it.get("checked"))
                    except Exception:
                        checked = False
                    if checked:
                        continue
                    if not is_consent_checkbox(hint=hint):
                        continue
                    attempted += 1
                    try:
                        loc = page.locator(selector).first
                        if loc.count() == 0:
                            continue
                        loc.check(timeout=8000)
                        filled += 1
                    except Exception:
                        continue
                    continue

                # Selects: choose the first non-empty, non-disabled option
                if tag == "select":
                    if value.strip():
                        continue
                    options = it.get("options") or []
                    chosen = None
                    if isinstance(options, list):
                        for o in options:
                            if not isinstance(o, dict):
                                continue
                            if o.get("disabled"):
                                continue
                            ov = str(o.get("value") or "").strip()
                            ol = str(o.get("label") or "").strip()
                            if ov:
                                chosen = {"value": ov, "label": ol}
                                break
                    if not chosen:
                        continue
                    attempted += 1
                    try:
                        loc = page.locator(selector).first
                        if loc.count() == 0:
                            continue
                        loc.select_option(value=chosen["value"], timeout=8000)
                        filled += 1
                    except Exception:
                        continue
                    continue

                # Text inputs/textareas
                v = pick_value(hint=hint, tag=tag, input_type=input_type, autocomplete=autocomplete, pattern_attr=pattern_attr)
                if v is None:
                    continue
                if value.strip():
                    continue
                attempted += 1
                try:
                    loc = page.locator(selector).first
                    if loc.count() == 0:
                        continue
                    loc.fill(v, timeout=8000)
                    filled += 1
                except Exception:
                    continue

            if filled:
                try:
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                return True, f"auto-fill: filled {filled}/{attempted} fields"
            return False, "auto-fill: nothing filled"

        def _auto_advance_next_step(page) -> tuple[bool, str, object]:
            """Best-effort: click 'Next Step' CTA to progress the journey.

            Charter is heavily assertion/intent-based; to actually reach backend calls we may need
            multiple consecutive 'Weiter' clicks (with occasional auto-fill) within one testcase.
            """
            if not _is_likely_ecom_page(page):
                return False, "auto-advance: not on eCom/checkout page", page

            before = redact_url_for_logging(getattr(page, "url", "") or "")
            selectors = [
                '[data-testid="cta-next-step"]',
                'button[data-testid="cta-next-step"]',
                'role=button name=Weiter',
            ]

            def _try_click(sel: str) -> bool:
                nonlocal page
                if sel.startswith("role="):
                    loc = page.get_by_role("button", name="Weiter")
                else:
                    loc = page.locator(sel)
                if loc.count() == 0:
                    return False
                btn = loc.first
                if not btn.is_visible():
                    return False
                try:
                    if not btn.is_enabled():
                        return False
                except Exception:
                    pass
                try:
                    btn.scroll_into_view_if_needed(timeout=5000)
                except Exception:
                    pass

                try:
                    with page.context.expect_page(timeout=2500) as new_page_info:
                        btn.click(timeout=10000, no_wait_after=True)
                    new_page = new_page_info.value
                    if new_page:
                        page = new_page
                except PlaywrightTimeoutError:
                    pass

                try:
                    page.wait_for_load_state('domcontentloaded', timeout=15000)
                except PlaywrightTimeoutError:
                    pass
                try:
                    page.wait_for_timeout(800)
                except Exception:
                    pass
                handle_cookie_banner(page)
                check_for_error_page(page)
                return True

            clicks = 0
            for attempt in range(1, 6):
                # Re-check: after a click, we might leave eCom.
                if not _is_likely_ecom_page(page):
                    break

                if auto_fill:
                    try:
                        ok_fill, msg_fill = _auto_fill_common_fields(page)
                        _net_mark("auto_fill", {"ok": bool(ok_fill), "message": msg_fill, "attempt": attempt})
                        alerts = _collect_ui_alerts(page)
                        if isinstance(alerts, dict) and int(alerts.get("count") or 0) > 0:
                            _net_mark("ui_alerts", {"attempt": attempt, **alerts})
                    except Exception:
                        pass

                clicked = False
                for sel in selectors:
                    try:
                        if _try_click(sel):
                            clicked = True
                            clicks += 1
                            break
                    except Exception:
                        continue
                if not clicked:
                    break

                # After click, capture any validation/inline error messages.
                try:
                    alerts = _collect_ui_alerts(page)
                    if isinstance(alerts, dict) and int(alerts.get("count") or 0) > 0:
                        _net_mark("ui_alerts", {"attempt": attempt, **alerts})
                except Exception:
                    pass

            after = redact_url_for_logging(getattr(page, "url", "") or "")
            if clicks > 0:
                if after and after != before:
                    return True, f"auto-advance: clicked {clicks}x; url changed", page
                return True, f"auto-advance: clicked {clicks}x; no url change observed", page

            # Fallback: inventory-based discovery click biased towards next-step semantics.
            try:
                inv = export_ui_inventory(page, Path(report_file).parent, prefix="ui_inventory_auto_advance")
                ok, reason, page = _try_discovery_click(page, {"text": "Weiter"}, inv, max_attempts=6)
                if ok:
                    return True, f"auto-advance: {reason}", page
            except Exception:
                pass
            return False, "auto-advance: Next Step CTA not found/enabled", page

        try:
            safe_url = redact_url_for_logging(url)
            print(f"--- Navigating to initial URL: {safe_url} ---")
            try:
                parts = urlsplit(url)
                had_query = bool(parts.query)
                had_fragment = bool(parts.fragment)
            except Exception:
                had_query = False
                had_fragment = False
            if had_query or had_fragment:
                print("  ℹ️ Hinweis: Query/Fragment wird in Logs/Artefakten redacted (Sicherheit).")
            _net_mark("goto", {"url": safe_url, "had_query": had_query, "had_fragment": had_fragment})
            page.goto(url, wait_until='domcontentloaded', timeout=60000)

            try:
                _stabilize_for_evidence(page, timeout_ms=20000)
            except Exception:
                pass

            # Setup evidence: always capture what the agent sees
            setup_initial_path = os.path.join(screenshots_dir, "_setup_00_initial.png")
            page.screenshot(path=setup_initial_path, full_page=True)
            print(f"  📸 Setup screenshot saved to {setup_initial_path}")

            # Initial checks after first load (Setup-Phase)
            handle_cookie_banner(page)

            setup_ready_path = os.path.join(screenshots_dir, "_setup_01_ready.png")
            page.screenshot(path=setup_ready_path, full_page=True)
            print(f"  📸 Setup screenshot saved to {setup_ready_path}")

            check_for_error_page(page)

            if pause_for_login:
                print("\n--- ⏸️ Pause für manuellen Login ---")
                print("Bitte logge dich jetzt im geöffneten Browserfenster ein (falls nötig).")
                print("Danach ENTER im Terminal drücken, um fortzufahren.")
                print("Hinweis: In nicht-interaktiven Terminals wird stattdessen gewartet.")
                try:
                    input("[pause-for-login] ENTER zum Fortfahren ... ")
                except EOFError:
                    sec = max(0, int(pause_for_login_seconds or 0))
                    print(f"[pause-for-login] Kein interaktives Terminal (EOF). Warte {sec}s und fahre fort...")
                    time.sleep(sec)
                setup_after_login_path = os.path.join(screenshots_dir, "_setup_02_after_login.png")
                page.screenshot(path=setup_after_login_path, full_page=True)
                print(f"  📸 Setup screenshot saved to {setup_after_login_path}")

                snap = _snapshot_form_inputs()
                if snap is not None:
                    (run_dir / "form_snapshot_after_login.json").write_text(
                        json.dumps(snap, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    try:
                        items = snap.get("items") or []
                        prefilled = 0
                        for it in items:
                            if not isinstance(it, dict):
                                continue
                            v = it.get("value") or {}
                            if isinstance(v, dict) and int(v.get("_len") or 0) > 0:
                                prefilled += 1
                        print(f"  🧾 Form snapshot after login saved (prefilled fields: {prefilled}/{len(items)})")
                    except Exception:
                        print("  🧾 Form snapshot after login saved")

                if verify_login:
                    print("  🔎 Verifiziere Login-Status via authproxy/user …")
                    ok = False
                    status = None
                    verified_url = None
                    try:
                        _net_mark("login_verification_start", {"timeout_seconds": int(verify_login_timeout_seconds or 0)})
                        try:
                            page.reload(wait_until='domcontentloaded', timeout=60000)
                        except Exception:
                            # Reload can fail in some redirect states; proceed to wait anyway.
                            pass

                        def _is_authproxy_user_ok(resp) -> bool:
                            try:
                                u = (resp.url or "").lower()
                                return ("/app/authproxy/" in u) and ("/user" in u) and int(resp.status) == 200
                            except Exception:
                                return False

                        resp = page.wait_for_response(_is_authproxy_user_ok, timeout=int(verify_login_timeout_seconds or 0) * 1000)
                        ok = True
                        status = int(resp.status)
                        verified_url = redact_url_for_logging(resp.url or "")
                    except Exception as e:
                        ok = False
                        status = None
                        verified_url = None
                        print(f"  ⚠️ Login-Verifikation nicht bestätigt (timeout/Fehler): {type(e).__name__}")
                    finally:
                        (run_dir / "login_verification.json").write_text(
                            json.dumps(
                                {
                                    "ok": ok,
                                    "status": status,
                                    "url": verified_url,
                                    "ts": _dt.datetime.now().isoformat(timespec="seconds"),
                                    "note": "Expected authproxy /user to return 200 after manual login.",
                                },
                                ensure_ascii=False,
                                indent=2,
                            ),
                            encoding="utf-8",
                        )
                        _net_mark("login_verification_result", {"ok": ok, "status": status, "url": verified_url})
            
            total_steps_executed = 0
            aborted = False

            for scenario in test_scenarios:
                if max_steps and total_steps_executed >= max_steps:
                    print(f"--- Reached max_steps limit ({max_steps}). Stopping test. ---")
                    break

                for test_case in scenario.get("testCases", []):
                    if max_steps and total_steps_executed >= max_steps:
                        break
                    if aborted:
                        break
                    
                    case_id = test_case.get("id")
                    print(f"--- Running Test Case: {case_id} ---")

                    for i, step in enumerate(test_case.get("steps", [])):
                        if max_steps and total_steps_executed >= max_steps:
                            break
                        if aborted:
                            break

                        action = step.get("action")
                        action_norm = normalize_action(action)
                        value = step.get("value")
                        testid = step.get("data-testid")
                        step_num = i + 1
                        step_id_text = f'{case_id}-Step{step_num}-{action.replace(" ", "")}'
                        current_step_id_for_net = step_id_text
                        _net_mark("step_start", {"case": case_id, "step_num": step_num, "action": action_norm, "url": redact_url_for_logging(getattr(page, "url", "") or "")})
                        screenshot_filename = f"{case_id}_Step-{step_num}_{action.replace(' ', '-')}.png"
                        screenshot_path = os.path.join(screenshots_dir, screenshot_filename)
                        
                        status = "Fail"
                        selector = ""
                        element = None
                        message = ""
                        try:
                            # For actions that don't interact with elements, handle them first.
                            if action_norm == "open_url":
                                # Execute charter Open URL deterministically to keep report/screenshots aligned.
                                open_target = _resolve_open_url(url, value)
                                if open_target:
                                    safe_open = redact_url_for_logging(open_target)
                                    print(f"    🌐 Open URL: navigating to {safe_open}")
                                    page.goto(open_target, wait_until='domcontentloaded', timeout=60000)
                                    try:
                                        handle_cookie_banner(page)
                                    except Exception:
                                        pass
                                    try:
                                        check_for_error_page(page)
                                    except Exception:
                                        pass
                                    try:
                                        _stabilize_for_evidence(page, timeout_ms=20000)
                                    except Exception:
                                        pass
                                    status = "Pass"
                                    element = "N/A"  # No element involved
                                    message = f"Open URL navigated to {safe_open}"
                                else:
                                    # Null/empty value means "stay here".
                                    try:
                                        _stabilize_for_evidence(page, timeout_ms=15000)
                                    except Exception:
                                        pass
                                    status = "Pass"
                                    element = "N/A"
                                    message = "Open URL: no-op (value is null/empty)"
                            elif action_norm == "wait":
                                wait_time = int(value)
                                print(f"    ⏳ Waiting for {wait_time} seconds...")
                                time.sleep(wait_time)
                                status = "Pass"
                                element = "N/A" # No element involved
                            elif action_norm == "intent":
                                # High-level agent step
                                page, status, message = execute_intent(page, step, run_dir=Path(report_file).parent)
                                element = "N/A"
                            else:
                                # For all other actions, we need to find an element.
                                if testid == "placeholder-testid" and not (step.get("aria-label") or step.get("aria_label") or step.get("selector") or step.get("role") or step.get("text") or step.get("name")):
                                    # We cannot locate an element without any hook.
                                    if inventory_on_placeholder:
                                        maybe_export_inventory(prefix=f"ui_inventory_{case_id}_{step_num}")
                                    status = "Warn"
                                    element = "N/A"
                                    message = "placeholder-testid: No locator provided. Add selector/data-testid/aria-label/role+name/text."
                                else:
                                    element, selector = find_element(page, step)
                                    if not element:
                                        # Special-case: user-provided stable checkout CTA pattern.
                                        # CTA is under [data-testid="summary-finance-wrapper"] and contains the ShoppingCart icon.
                                        step_selector = str(step.get("selector") or "")
                                        step_text = str(step.get("text") or "")
                                        targets_checkout_cta = (
                                            "summary-finance-wrapper" in step_selector
                                            or "Online leasen" in step_text
                                            or "icon-ShoppingCart" in step_selector
                                        )
                                        if targets_checkout_cta:
                                            opened = ensure_summary_open(page)
                                            if opened:
                                                element, selector = find_element(page, step)

                                        if not element:
                                            # Agent-like: for click steps, try an auto-repair click from inventory.
                                            if action_norm == "click" and auto_repair_click:
                                                inv = maybe_export_inventory(prefix=f"ui_inventory_{case_id}_{step_num}_autofix")
                                                ok = False
                                                reason = ""
                                                if inv:
                                                    ok, reason = _try_auto_repair_click(page, step, inv)
                                                if not ok and discovery_click and inv:
                                                    ok, reason, page = _try_discovery_click(page, step, inv, max_attempts=6)

                                                if ok:
                                                    status = "Warn"
                                                    element = "N/A"
                                                    message = reason
                                                else:
                                                    cand_summary = _summarize_candidates(inv or {}, limit=6) if inv else ""
                                                    raise PlaywrightTimeoutError(
                                                        "Could not find element using provided locators "
                                                        f"(data-testid='{testid}', aria-label='{step.get('aria-label') or step.get('aria_label')}', role='{step.get('role')}', name='{step.get('name')}', text='{step.get('text')}', selector='{step.get('selector')}'). "
                                                        + (f"Top candidates: {cand_summary}" if cand_summary else "")
                                                    )
                                            else:
                                                raise PlaywrightTimeoutError(
                                                    "Could not find element using provided locators "
                                                    f"(data-testid='{testid}', aria-label='{step.get('aria-label') or step.get('aria_label')}', role='{step.get('role')}', name='{step.get('name')}', text='{step.get('text')}', selector='{step.get('selector')}')."
                                                )

                                    if element != "N/A":
                                        print(f"  Step {step_num}: {action} on '{selector}'")

                                if element != "N/A" and action_norm == "check":
                                    if element.is_visible():
                                        print(f"    ✅ Check successful for selector: {selector}")
                                        status = "Pass"
                                    else:
                                        print(f"    ❌ Element found but not visible for selector: {selector}")
                                        status = "Fail"
                                elif element != "N/A" and action_norm == "click":
                                    new_page = None

                                    step_selector = str(step.get("selector") or "")
                                    step_text = str(step.get("text") or "")
                                    targets_checkout_cta = (
                                        "summary-finance-wrapper" in step_selector
                                        or "Online leasen" in step_text
                                        or "icon-ShoppingCart" in step_selector
                                    )

                                    # Make CTA clicks more resilient (offscreen/late-rendered).
                                    try:
                                        element.scroll_into_view_if_needed(timeout=5000)
                                    except Exception:
                                        pass
                                    try:
                                        element.wait_for(state="visible", timeout=8000)
                                    except Exception:
                                        # We'll still attempt the click; some SPAs report visible late.
                                        pass

                                    # One click, but capture a newly opened tab/page if it happens.
                                    try:
                                        with page.context.expect_page(timeout=3000) as new_page_info:
                                            if targets_checkout_cta:
                                                element.click(timeout=10000, no_wait_after=True)
                                            else:
                                                element.click(timeout=10000)
                                        new_page = new_page_info.value
                                    except PlaywrightTimeoutError as e:
                                        # Two different timeout classes can land here:
                                        # 1) expect_page timed out (no new tab) AFTER a successful click
                                        # 2) the click itself timed out
                                        msg = str(e)
                                        if "locator.click" in msg.lower():
                                            if targets_checkout_cta:
                                                element.click(timeout=3000, force=True, no_wait_after=True)
                                            else:
                                                raise
                                        # else: no new page opened; continue on same page
                                    except Exception:
                                        # As a last resort for the checkout CTA, try a forced click.
                                        if targets_checkout_cta:
                                            element.click(timeout=3000, force=True, no_wait_after=True)
                                        else:
                                            raise

                                    if new_page:
                                        page = new_page
                                        print("    ✅ Click opened a new page/tab. Switching context.")
                                    else:
                                        print(f"    ✅ Click successful on selector: {selector}")

                                    print(f"    ⏳ Waiting for navigation and checks...")
                                    try:
                                        page.wait_for_load_state('domcontentloaded', timeout=15000)
                                    except PlaywrightTimeoutError:
                                        # SPA transitions may not trigger a full load; proceed with checks.
                                        pass
                                    handle_cookie_banner(page)
                                    check_for_error_page(page)
                                    print(f"    ✅ Navigation and checks complete.")
                                    status = "Pass"
                                elif element != "N/A" and action_norm == "fill":
                                    element.fill(value, timeout=10000)
                                    print(f"    ✅ Fill successful on selector: {selector}")
                                    status = "Pass"
                                elif status == "Warn":
                                    # already handled
                                    pass
                                else:
                                    message = message or f"Unsupported action: {action}"
                                    status = "Warn"
                            
                        except PlaywrightTimeoutError as e:
                            print(f"    ❌ TIMEOUT on Step {step_num}: {action}. {e.message.splitlines()[0]}")
                            status = "Fail"
                            maybe_export_inventory(prefix=f"ui_inventory_{case_id}_{step_num}_timeout")
                            message = message or e.message.splitlines()[0]
                        except Exception as e:
                            print(f"    ❌ ERROR on Step {step_num}: {action} on '{selector}'. {e}")
                            status = "Fail"
                            message = str(e).splitlines()[0]
                            maybe_export_inventory(prefix=f"ui_inventory_{case_id}_{step_num}_error")
                        
                        finally:
                            # Totals + Findings (Triage)
                            if action_norm not in ["open_url"]:
                                totals["steps_total"] += 1
                                if status.lower() == "pass":
                                    totals["pass"] += 1
                                elif status.lower() == "warn":
                                    totals["warn"] += 1
                                else:
                                    totals["fail"] += 1

                            if status in {"Fail", "Warn"}:
                                is_error_page = ("Critical Error: Detected" in (message or ""))
                                is_timeout = status == "Fail" and "timeout" in (message or "").lower()
                                kind, severity = classify_finding(
                                    message=message,
                                    is_timeout=is_timeout,
                                    is_error_page=is_error_page,
                                )
                                findings.append(
                                    {
                                        "kind": kind,
                                        "severity": severity,
                                        "case_id": case_id,
                                        "step_num": step_num,
                                        "action": action,
                                        "selector": selector,
                                        "summary": message or f"{status} on {selector}",
                                        "screenshot": Path(screenshot_path).name,
                                    }
                                )

                            # Agent-like: abort early on blockers to avoid noisy runs.
                            if stop_on_blocker and status == "Fail" and action_norm not in ["open_url", "wait"]:
                                totals["aborted"] = True
                                totals["abort_reason"] = message or "blocker"
                                aborted = True

                            should_count_step = action_norm not in ["open_url"]
                            if should_count_step:
                                total_steps_executed += 1
                            # Always take a screenshot for evidence (also for Open URL / Wait steps)
                            try:
                                _stabilize_for_evidence(page, timeout_ms=15000)
                            except Exception:
                                pass
                            page.screenshot(path=screenshot_path)
                            print(f"    📸 Screenshot saved to {screenshot_path}")

                            # Update the HTML report after each step
                            update_report(
                                report_file,
                                step_id_text,
                                status,
                                screenshot_path=screenshot_path,
                                message=message,
                            )
                            print(f"    📝 Report updated for step: {step_id_text} with status: {status}")

                            _net_mark("step_end", {"status": status, "message": (message[:200] if isinstance(message, str) else "")})

                    # Journey progression: if the charter contains mostly assertions/intents,
                    # auto-advance keeps the run from staying on the same screen forever.
                    if auto_advance and not aborted and _is_journey_driver_test_case(test_case):
                        try:
                            ok_adv, msg_adv, page = _auto_advance_next_step(page)
                            if ok_adv:
                                _net_mark("auto_advance", {"ok": True, "message": msg_adv})
                            else:
                                _net_mark("auto_advance", {"ok": False, "message": msg_adv})
                        except Exception:
                            pass

                    if aborted:
                        print(f"--- 🛑 Aborting run early due to blocker: {totals.get('abort_reason','')} ---")
                        break

                if aborted:
                    break

            if aborted:
                pass

        except Exception as e:
            print(f"--- ❌ A critical error occurred: {e} ---")

        finally:
            browser.close()
            print("--- Smoketest finished ---")

    finished_at = _dt.datetime.now().isoformat(timespec="seconds")
    try:
        run_dir = Path(report_file).parent
        try:
            findings.extend(write_technical_checkpoints(run_dir))
        except Exception:
            pass
        try:
            write_dataflow_inventory(run_dir)
        except Exception:
            pass
        write_run_meta(run_dir, url=url, charter_file=charter_file, started_at=started_at, finished_at=finished_at, totals=totals)
        write_findings(run_dir, findings=findings, report_file=report_file)
        write_summary(run_dir, totals=totals, report_file=report_file)
        print(f"--- ✅ Summary/Findings written to: {run_dir} ---")
    except Exception as e:
        print(f"--- ⚠️ Could not write summary/findings: {e} ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Execute a smoketest based on a JSON charter file.')
    parser.add_argument('--url', type=str, required=False, default=None, help='The starting URL for the test (full URL). If omitted, you will be prompted unless --prompt-for-url is false and the environment is non-interactive.')
    parser.add_argument('--prompt-for-url', action='store_true', help='Prompt interactively for a dynamic start URL (recommended when configurator links change often).')
    parser.add_argument('--charter-file', type=Path, required=True, help='Path to the JSON charter file.')
    parser.add_argument('--report-file', type=Path, required=False, default=None, help='Path to the HTML report file to update. If omitted, a new run folder is created under results-root.')
    parser.add_argument('--screenshots-dir', type=Path, required=False, default=None, help='Directory to save screenshots. If omitted, uses <run>/screenshots under results-root.')
    parser.add_argument('--results-root', type=Path, required=False, default=Path('results') / 'bto-checkout' / 'runs', help='Root folder for new runs when report-file/screenshots-dir are omitted.')
    parser.add_argument('--run-id', type=str, required=False, default=None, help='Optional run id (folder name). Default: timestamp.')
    parser.add_argument('--max-steps', type=int, default=None, help='Maximum number of steps to execute. Use 0 or a negative value for unlimited (run full charter).')
    parser.add_argument('--continue-on-fail', action='store_true', help='Continue executing steps even after failures (no early abort).')
    parser.add_argument('--inventory-max', type=int, default=3, help='Maximum number of UI inventory exports per run.')
    parser.add_argument('--inventory-on-placeholder', action='store_true', help='Export UI inventory for placeholder steps without locators (can be noisy).')
    parser.add_argument('--no-auto-repair-click', action='store_true', help='Disable auto-repair attempts for click steps based on UI inventory.')
    parser.add_argument('--no-discovery-click', action='store_true', help='Disable discovery click strategy (trying top CTA candidates).')
    parser.add_argument('--headed', action='store_true', help='Run browser headed (useful for debugging bot-detection/visibility issues).')
    parser.add_argument('--slowmo-ms', type=int, default=0, help='Slow down actions by N ms (headed runs).')
    parser.add_argument('--no-stealth', action='store_true', help='Disable lightweight stealth tweaks.')
    parser.add_argument('--pause-for-login', action='store_true', help='Pause after initial load to allow manual login in the headed browser window.')
    parser.add_argument('--pause-for-login-seconds', type=int, default=180, help='Fallback wait time (seconds) if terminal is non-interactive.')
    parser.add_argument('--no-verify-login', action='store_true', help='Disable post-login verification (waiting for authproxy /user 200).')
    parser.add_argument('--verify-login-timeout-seconds', type=int, default=20, help='Seconds to wait for authproxy /user 200 after manual login.')
    parser.add_argument('--auto-advance', dest='auto_advance', action='store_true', default=None, help='Auto-click Next Step CTA at the end of each test case to progress the journey.')
    parser.add_argument('--no-auto-advance', dest='auto_advance', action='store_false', default=None, help='Disable auto-advance even for full-charter runs.')
    parser.add_argument('--auto-fill', dest='auto_fill', action='store_true', default=None, help='Best-effort fill common personal data fields (first/last name, email) to enable Next Step CTA.')
    parser.add_argument('--no-auto-fill', dest='auto_fill', action='store_false', default=None, help='Disable auto-fill even when auto-advance is enabled.')
    
    args = parser.parse_args()

    start_url = args.url
    if args.prompt_for_url or not start_url:
        try:
            start_url = input("Start-URL eingeben (vollständig, inkl. Query): ").strip()
        except EOFError:
            start_url = (start_url or "").strip()
            if not start_url:
                raise SystemExit("No start URL provided and cannot prompt in non-interactive terminal. Use --url <URL>.")
    if not start_url:
        raise SystemExit("Empty start URL. Provide --url <URL> or use --prompt-for-url.")
    
    run_dir, report_file, screenshots_dir = prepare_run_paths(
        results_root=args.results_root,
        run_id=args.run_id,
        charter_file=args.charter_file,
        start_url=start_url,
        report_file=args.report_file,
        screenshots_dir=args.screenshots_dir,
    )
    ensure_report_exists(report_file, args.charter_file)

    max_steps = args.max_steps
    if isinstance(max_steps, int) and max_steps <= 0:
        max_steps = None

    auto_advance = args.auto_advance
    if auto_advance is None:
        # Default: when running the full charter (no max_steps) and not aborting early,
        # auto-advance is required to actually progress the journey.
        auto_advance = (max_steps is None) and bool(args.continue_on_fail)

    auto_fill = args.auto_fill
    if auto_fill is None:
        auto_fill = bool(auto_advance)

    run_smoketest(
        start_url,
        args.charter_file,
        report_file,
        screenshots_dir,
        max_steps,
        stop_on_blocker=not args.continue_on_fail,
        inventory_max=args.inventory_max,
        inventory_on_placeholder=args.inventory_on_placeholder,
        auto_repair_click=not args.no_auto_repair_click,
        discovery_click=not args.no_discovery_click,
        headed=args.headed,
        slowmo_ms=args.slowmo_ms,
        stealth=not args.no_stealth,
        pause_for_login=args.pause_for_login,
        pause_for_login_seconds=args.pause_for_login_seconds,
        verify_login=not args.no_verify_login,
        verify_login_timeout_seconds=args.verify_login_timeout_seconds,
        auto_advance=auto_advance,
        auto_fill=auto_fill,
    )
