import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup


@dataclass
class StepResult:
    case_id: str
    step_num: int
    step_id: str
    action_norm: str
    intent: str | None
    status: str
    message: str
    atomic: dict | None = None


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    out: list[dict] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def _norm_status(s: str) -> str:
    s = (s or "").strip().lower()
    if s in {"pass", "fail", "warn", "unknown"}:
        return s
    # map runner style
    if s == "not run":
        return "unknown"
    return "unknown"


def _status_from_step(step: StepResult) -> str:
    return _norm_status(step.status)


def _find_best_step(steps: list[StepResult], *, intent: str) -> StepResult | None:
    # Pick the last step with that intent (latest evidence)
    for s in reversed(steps):
        if (s.intent or "").strip().lower() == intent.strip().lower():
            return s
    return None


def _infer_bullet(case_id: str, bullet_text: str, case_steps: list[StepResult]) -> tuple[str, str]:
    """Returns (status, note).

    Conservative: only mark pass if the automation truly asserts the bullet.
    Otherwise use warn with an explicit limitation note or keep unknown.
    """
    t = (bullet_text or "").strip()
    tl = t.lower()

    def note_from_step(step: StepResult, extra: str) -> str:
        base = f"Auto via {step.step_id}: {step.status}. {step.message}".strip()
        if extra:
            return (base + " | " + extra).strip()
        return base

    # Tab slider related
    if any(k in tl for k in ["tab slider", "tabs", "sliding", "arrows", "arrow"]):
        step = _find_best_step(case_steps, intent="assert_tab_slider_present")
        if not step:
            return "unknown", "Keine passende Intent-Ausführung im Run gefunden."

        # Prefer atomic sub-results when available.
        try:
            atomic = step.atomic or {}
            tab = atomic.get("tab_slider") or {}
            many_tabs = str(tab.get("many_tabs") or "").lower()
            deactivated = str(tab.get("has_deactivated_tabs") or "").lower()
            arrows = str(tab.get("arrows_functional") or "").lower()
            if many_tabs or deactivated or arrows:
                if "cover" in tl or "many" in tl:
                    # Spec-Lock: "many" / "cover all" is not a numeric threshold unless the human defines it.
                    # We do not convert this into a hard min-tabs assumption.
                    return "unknown", note_from_step(step, "SPEC_REQUIRED: 'many/cover all journey steps' needs human threshold/definition")
                if "deactiv" in tl:
                    st = deactivated if deactivated in {"pass", "fail", "warn", "unknown"} else "unknown"
                    return st, note_from_step(step, f"atomic deactivated_tabs={deactivated}")
                if "arrow" in tl or "arrows" in tl or "sliding" in tl:
                    st = arrows if arrows in {"pass", "fail", "warn", "unknown"} else "unknown"
                    return st, note_from_step(step, f"atomic arrows_functional={arrows}")
        except Exception:
            pass

        st = _status_from_step(step)
        if st == "fail":
            return "fail", note_from_step(step, "Tab-Slider nicht gefunden.")
        if st == "warn":
            return "warn", note_from_step(step, "Tab-Slider nicht bestätigt (Variant?).")
        if st == "pass":
            # Presence check only. Do NOT claim semantic coverage.
            if "cover all" in tl or "cover" in tl:
                return "warn", note_from_step(step, "Nur Presence/Visibility geprüft; keine Abdeckung aller Journey-Steps validiert.")
            if "deactiv" in tl:
                return "warn", note_from_step(step, "Nur Presence/Visibility geprüft; kein Disabled-State (aria-disabled/disabled) validiert.")
            if "arrow" in tl or "arrows" in tl or "sliding" in tl:
                return "warn", note_from_step(step, "Nur Presence/Visibility geprüft; Pfeil-Interaktion/Scroll-Änderung nicht validiert.")
            return "warn", note_from_step(step, "Nur Presence/Visibility geprüft; Semantik nicht validiert.")

    # Configurator CTA (start eCom journey)
    if any(k in tl for k in ["ecom cta", "cta for starting", "starting the ecommerce journey", "starts the corresponding ecommerce journey", "clicking on the ecom cta"]):
        step = _find_best_step(case_steps, intent="start_checkout")
        if step:
            st = _status_from_step(step)
            if st == "fail":
                return "fail", note_from_step(step, "CTA konnte nicht gefunden/geklickt werden.")
            if st == "warn":
                return "warn", note_from_step(step, "CTA-Click best-effort; Ergebnis/Navigation nicht eindeutig bestätigt.")
            # pass
            if "active" in tl or "clickable" in tl:
                return "pass", note_from_step(step, "Automatisch: CTA gefunden und Click ausgeführt.")
            if "clicking" in tl or "starts" in tl:
                msg_l = (step.message or "").lower()
                if any(x in msg_l for x in ["new page opened", "url changed", "ecom markers found"]):
                    return "pass", note_from_step(step, "Automatisch: Click führte zu Navigation/Transition.")
                return "warn", note_from_step(step, "Click ausgeführt, aber Navigation/Transition nicht eindeutig bestätigt.")
            # availability
            return "pass", note_from_step(step, "Automatisch: CTA gefunden (implizit durch erfolgreichen Click).")

    # Price box related
    if any(k in tl for k in ["price box", "angebot", "price"]):
        step = _find_best_step(case_steps, intent="assert_price_box_present")
        if not step:
            return "unknown", "Keine passende Intent-Ausführung im Run gefunden."
        st = _status_from_step(step)
        if st == "pass":
            return "warn", note_from_step(step, "Automatisch: Anker/CTA im Price-Box-Bereich sichtbar; Inhalte (Werte/Backend-Abgleich) nicht validiert.")
        return st, note_from_step(step, "")

    # Sticky bar / next step (keep keywords specific; 'CTA' alone is too broad)
    if any(k in tl for k in ["sticky bar", "sticky", "next step", "nächster schritt", "cta-next-step"]):
        step = _find_best_step(case_steps, intent="assert_sticky_bar_present")
        if not step:
            return "unknown", "Keine passende Intent-Ausführung im Run gefunden."
        st = _status_from_step(step)
        if st == "pass":
            return "warn", note_from_step(step, "Automatisch: CTA sichtbar; Enablement/Business-Logik nicht voll validiert.")
        return st, note_from_step(step, "")

    # Checkout loaded / opened
    if any(k in tl for k in ["opens", "opened", "checkout", "personal data tab", "starts with"]):
        step = _find_best_step(case_steps, intent="assert_checkout_loaded")
        if not step:
            return "unknown", "Keine passende Intent-Ausführung im Run gefunden."
        st = _status_from_step(step)
        if st == "pass":
            # We check checkout.html + anchors, not the actual selected tab.
            extra = "Automatisch: checkout/eCom-Anker geprüft; 'Personal data tab' (aktive Auswahl) nicht explizit asserted."
            return "warn", note_from_step(step, extra)
        return st, note_from_step(step, "")

    # Default: no reliable automation mapping.
    return "unknown", "Für dieses Bullet existiert aktuell keine robuste automatische Zuordnung/Assertion." 


def _update_checklist_for_case(soup: BeautifulSoup, *, case_id: str, statuses: list[tuple[str, str, str]]) -> int:
    """statuses: list of (bullet_text, status, note). Returns number of updated items."""
    updated = 0
    h3 = soup.find("h3", id=f"case-{case_id}")
    if not h3:
        return 0

    container = h3.find_next("div")
    if not container:
        return 0

    ul = container.find("ul", class_="checklist")
    if not ul:
        return 0

    lis = ul.find_all("li")
    for li in lis:
        text_span = li.find_all("span")
        if not text_span or len(text_span) < 2:
            continue
        bullet = (text_span[1].get_text(" ", strip=True) or "").strip()
        if not bullet:
            continue

        match = None
        for (b, st, note) in statuses:
            if b == bullet:
                match = (st, note)
                break
        if not match:
            continue

        st, note = match
        icon = li.find("span", class_="status-icon")
        if not icon:
            continue
        icon["data-status"] = st
        if note:
            # Tooltips work in the report UI without changing JS.
            icon["title"] = note
        updated += 1

    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a BTO smoketest run, fill atomic checklist items in the HTML report, and write actionable feedback.")
    parser.add_argument("--run-dir", type=Path, required=True, help="Run directory under results/bto-checkout/runs/<run-id>/")
    parser.add_argument("--update-report", action="store_true", help="Update BTO_Test_Report_v1.0.html checklist items in-place.")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    report_path = run_dir / "BTO_Test_Report_v1.0.html"
    meta_path = run_dir / "run_meta.json"
    steps_path = run_dir / "step_results.jsonl"

    if not run_dir.exists():
        raise SystemExit(f"Run dir not found: {run_dir}")
    if not report_path.exists():
        raise SystemExit(f"Report not found: {report_path}")
    if not meta_path.exists():
        raise SystemExit(f"run_meta.json not found: {meta_path}")
    if not steps_path.exists():
        raise SystemExit(f"step_results.jsonl not found: {steps_path} (run needs updated runner)")

    meta = _read_json(meta_path)

    # Prefer the copied charter in run inputs to keep analysis reproducible.
    inputs_dir = run_dir / "inputs"
    charter_path = None
    if inputs_dir.exists():
        for p in inputs_dir.glob("*.json"):
            # choose first json that looks like the charter (contains testScenario/testCases)
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(obj, list) and obj and isinstance(obj[0], dict) and "testScenario" in obj[0]:
                    charter_path = p
                    break
            except Exception:
                continue
    if not charter_path:
        # fallback to meta path (workspace relative)
        try:
            charter_path = Path(str(meta.get("charter_file") or "")).resolve()
        except Exception:
            charter_path = None

    if not charter_path or not Path(charter_path).exists():
        raise SystemExit("Charter file not found for analysis (run inputs missing and run_meta charter_file not resolvable).")

    charter = json.loads(Path(charter_path).read_text(encoding="utf-8"))
    step_rows = _read_jsonl(steps_path)

    steps_by_case: dict[str, list[StepResult]] = {}
    for r in step_rows:
        case_id = str(r.get("case_id") or "").strip()
        if not case_id:
            continue
        try:
            steps_by_case.setdefault(case_id, []).append(
                StepResult(
                    case_id=case_id,
                    step_num=int(r.get("step_num") or 0),
                    step_id=str(r.get("step_id") or ""),
                    action_norm=str(r.get("action_norm") or ""),
                    intent=(str(r.get("intent")) if r.get("intent") else None),
                    status=str(r.get("status") or "unknown"),
                    message=str(r.get("message") or ""),
                    atomic=(r.get("atomic") if isinstance(r.get("atomic"), dict) else None),
                )
            )
        except Exception:
            continue

    # Build bullet status proposals per case from charter descriptions.
    proposals: dict[str, list[tuple[str, str, str]]] = {}
    total_bullets = 0
    total_pass = total_warn = total_fail = total_unknown = 0

    for scenario in charter:
        for tc in scenario.get("testCases", []) or []:
            case_id = str(tc.get("id") or "").strip()
            if not case_id:
                continue
            desc = str(tc.get("description") or "")
            bullets: list[str] = []
            for line in desc.splitlines():
                line = line.strip()
                if line.startswith("-"):
                    bullets.append(line.strip("- "))

            if not bullets:
                continue

            case_steps = steps_by_case.get(case_id, [])
            entries: list[tuple[str, str, str]] = []
            for b in bullets:
                st, note = _infer_bullet(case_id, b, case_steps)
                entries.append((b, st, note))
                total_bullets += 1
                if st == "pass":
                    total_pass += 1
                elif st == "warn":
                    total_warn += 1
                elif st == "fail":
                    total_fail += 1
                else:
                    total_unknown += 1

            proposals[case_id] = entries

    soup = BeautifulSoup(report_path.read_text(encoding="utf-8"), "html.parser")
    updated = 0
    if args.update_report:
        for case_id, entries in proposals.items():
            updated += _update_checklist_for_case(soup, case_id=case_id, statuses=entries)
        report_path.write_text(str(soup.prettify()), encoding="utf-8")

    # Write feedback summary for humans.
    lines: list[str] = []
    lines.append("# Post-Run Agent Feedback")
    lines.append("")
    lines.append(f"- Run dir: {run_dir.as_posix()}")
    lines.append(f"- Report: {report_path.name}")
    lines.append(f"- Start URL (redacted): {meta.get('url','')}")
    lines.append("")
    lines.append("## Atomare Checklist (Auto-Auswertung)")
    lines.append("")
    lines.append(f"- Bullets total: {total_bullets}")
    lines.append(f"- pass: {total_pass}")
    lines.append(f"- warn (teilweise/limitiert): {total_warn}")
    lines.append(f"- fail: {total_fail}")
    lines.append(f"- unknown (nicht automatisiert zuordenbar): {total_unknown}")
    if args.update_report:
        lines.append(f"- HTML checklist items updated: {updated}")
    lines.append("")

    # Actionable next steps: show a short list of the worst offenders.
    lines.append("## Handlungshinweise")
    lines.append("")

    # Prioritize: fails, then unknown, then warn
    def _iter_sorted():
        for cid, entries in proposals.items():
            for (b, st, note) in entries:
                yield cid, b, st, note

    items = list(_iter_sorted())
    order = {"fail": 0, "unknown": 1, "warn": 2, "pass": 3}
    items.sort(key=lambda x: (order.get(x[2], 99), x[0]))

    shown = 0
    for cid, b, st, note in items:
        if st == "pass":
            continue
        # Keep it short; deep details stay in the HTML tooltips.
        lines.append(f"- {cid}: [{st}] {b}")
        if note:
            lines.append(f"  - Evidence/Limit: {note}")
        shown += 1
        if shown >= 12:
            break

    lines.append("")
    lines.append("## Empfehlung: Automatisierungs-Lücken schließen")
    lines.append("")
    lines.append("- Für Bullets mit warn/unknown: Charter in atomare Intents auftrennen und im Runner echte Assertions implementieren (z.B. Tab-Anzahl, Disabled-State, Pfeil-Interaktion mit messbarer Scroll-Änderung).")
    lines.append("- Bis dahin: warn/unknown sind bewusst nicht 'beschönigt' – sie zeigen, wo menschliche Review-Zeit nötig ist.")

    feedback_path = run_dir / "agent_feedback.md"
    feedback_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("--- Post-Run Agent ---")
    print(f"Updated checklist items: {updated}")
    print(f"Feedback written: {feedback_path}")


if __name__ == "__main__":
    main()
