import argparse
import datetime as dt
import json
from pathlib import Path


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _bullets(text: str) -> list[str]:
    out: list[str] = []
    for line in (text or "").splitlines():
        s = line.strip()
        if s.startswith("-"):
            b = s.strip("- ").strip()
            if b:
                out.append(b)
    return out


def _has_intent_steps(steps) -> bool:
    for s in steps or []:
        if str(s.get("action") or "").strip().lower() == "intent":
            return True
    return False


def _scenario_tags(scenario_name: str) -> set[str]:
    sn = (scenario_name or "").lower()
    tags = set()
    for key in [
        "personal data",
        "volkswagen partner",
        "pick up",
        "summary",
        "thank you",
        "sticky bar",
        "disclaimer",
        "price box",
        "tab slider",
        "fsag",
    ]:
        if key in sn:
            tags.add(key)
    return tags


def _suggest_for_case(case_id: str, scenario_name: str, desc: str) -> tuple[list[dict], list[str]]:
    """Return (suggested_intents, notes). Intents are abstract and future-proof by design."""
    bullets = _bullets(desc)
    text = (desc or "").lower()
    tags = _scenario_tags(scenario_name)

    intents: list[dict] = []
    notes: list[str] = []

    def add(intent: str, name: str, **args):
        step = {"action": "intent", "intent": intent, "name": name}
        if args:
            step.update(args)
        intents.append(step)

    # Baseline: ensure we're on checkout page
    add("assert_checkout_loaded", "eCom page loaded")

    # High-level routing by scenario/tags
    if "price box" in tags:
        add("assert_price_box_present", "price box")

    if "sticky bar" in tags:
        add("assert_sticky_bar_present", "sticky bar / next step")
        if "sticks" in text or "scroll" in text or "footer" in text:
            add(
                "assert_sticky_behavior_on_scroll",
                "sticky sticks until footer",
                spec_required=True,
            )
            notes.append(
                "SPEC_REQUIRED: Definition 'sticks' (BoundingBox/CSS) + Definition 'footer accessed' (Intersection/scroll position)."
            )
        if "always leads" in text or ("next step" in text and "completed" in text):
            add(
                "assert_next_step_navigation_when_completed",
                "next step leads to next step when completed",
                spec_required=True,
            )
            notes.append(
                "SPEC_REQUIRED: Definition 'current step completed' (required fields valid / CTA enabled / state)."
            )

    if "disclaimer" in tags or "co2" in text:
        add("assert_disclaimer_references", "disclaimer references", spec_required=True)
        add("assert_disclaimer_texts", "disclaimer texts", spec_required=True)
        if "summary" in tags or "summary step" in text:
            add("assert_summary_co2_disclaimer", "CO2 disclaimer in summary", spec_required=True)
        notes.append("SPEC_REQUIRED: genaue Disclaimer-Refs (Anzahl/Position) und Mapping Ref→Text definieren.")

    if "tab slider" in tags or "tab slider" in text:
        add("assert_tab_slider_present", "tab slider")
        notes.append("SPEC_REQUIRED: Definition für 'many tabs' und 'cover all steps' (Threshold/Mapping).")

    if "personal data" in tags:
        add("assert_active_tab", "active tab is personal data", tab="personal data", spec_required=True)
        add("fill_personal_data_required", "fill mandatory personal data", email="test@test.de", spec_required=True)
        add("assert_next_step_gate", "cannot proceed until mandatory fields valid", spec_required=True)
        notes.append("SPEC_REQUIRED: Tab-Erkennung (Selector/Role/Label) + Pflichtfelder/Fehlermeldungen.")

    if "volkswagen partner" in tags:
        add("navigate_to_tab", "go to Volkswagen partner", tab="volkswagen partner", spec_required=True)
        if "search" in text or "postal" in text or "cities" in text:
            add("search_dealer", "search dealer by city/postal", query="<TODO>", spec_required=True)
            add("assert_dealer_results", "dealer results >= N", min_results="<TODO>", spec_required=True)
        if "selection" in text or "select" in text:
            add("select_dealer", "select first dealer result", strategy="first", spec_required=True)
        notes.append("SPEC_REQUIRED: stabile Dealer-Search-Selector + Definition 'many corresponding results'.")

    if "pick up" in tags:
        add("navigate_to_tab", "go to Pick up", tab="pick up", spec_required=True)
        add("assert_pickup_options", "pickup options present", spec_required=True)
        if "transfer" in text or "cost" in text:
            add("assert_transfer_costs", "transfer costs displayed", spec_required=True)
        if "selection" in text or "select" in text:
            add("select_pickup", "select pickup option", strategy="first", spec_required=True)
        notes.append("SPEC_REQUIRED: Pickup-Options/Selectors und Erwartungstexte.")

    if "summary" in tags:
        add("navigate_to_tab", "go to Summary", tab="summary", spec_required=True)
        add("assert_summary_sections", "summary sections present", sections="<TODO>", spec_required=True)
        if "expanding" in text or "collaps" in text:
            add("assert_summary_section_collapsible", "sections expandable/collapsible", spec_required=True)
        notes.append("SPEC_REQUIRED: welche Summary-Sektionen, welche Überschriften/IDs, welche Inhalte genau.")

    if "thank you" in tags:
        add("navigate_to_tab", "go to Thank You", tab="thank you", spec_required=True)
        add("assert_thank_you", "thank you content present", spec_required=True)
        if "email" in text:
            add("assert_confirmation_email_trigger", "confirmation email triggered", spec_required=True)
        notes.append("SPEC_REQUIRED: deterministische Thank-You Marker + Email-Signal (UI/Network).")

    if "fsag" in tags or "fsag" in text:
        add("assert_duc_entrypoint_captured", "FSAG entry URL captured", spec_required=True)
        notes.append("Hinweis: VPN-only Schritte ggf. als optional markieren; URLs immer redacted speichern.")

    # Price box edit flow
    if "edit" in text or "enable the editing" in text or "financing layer" in text:
        add("open_financing_layer", "open financing layer", spec_required=True)
        add("change_financing_parameter", "change financing parameter", parameter="<TODO>", value="<TODO>", spec_required=True)
        add("assert_price_box_updated", "price box updated", spec_required=True)
        notes.append("SPEC_REQUIRED: welche Parameter (km/Laufzeit/Anzahlung) und wie UI→Quelle vergleichen.")

    # De-duplicate consecutive identical intents
    compact: list[dict] = []
    seen = set()
    for s in intents:
        key = (s.get("intent"), s.get("tab"), s.get("name"))
        if key in seen:
            continue
        seen.add(key)
        compact.append(s)

    # Keep only the essentials if we overshot.
    return compact, notes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--charter",
        default=str(Path("prompts/testdata/bto/v1.0/charter.json")),
        help="Path to charter.json",
    )
    ap.add_argument(
        "--outdir",
        default=str(Path("results/bto-checkout/reports")),
        help="Output directory",
    )
    args = ap.parse_args()

    charter_path = Path(args.charter)
    charter = _load_json(charter_path)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    ts = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    md_path = outdir / f"intent_suggestions_{ts}.md"
    latest_md = outdir / "latest_intent_suggestions.md"

    suggestions: list[dict] = []

    lines: list[str] = []
    lines.append("# Intent-Vorschläge (testweise)\n")
    lines.append(f"- Zeitpunkt: {dt.datetime.now().isoformat(timespec='seconds')}\n")
    lines.append(f"- Charter: {charter_path.as_posix()}\n")
    lines.append("\n## Prinzipien (future-proof)\n")
    lines.append("- Intents sind **abstrakt** (Was?), nicht UI-fragil (Wie genau?).\n")
    lines.append("- Bevorzugte Locator-Reihenfolge: `data-testid` → ARIA Role+Name → sichtbarer Text (Regex) → Inventory/Discovery.\n")
    lines.append("- Alles, was nicht deterministisch definierbar ist, bleibt `SPEC_REQUIRED` und wird nicht schöngeredet.\n")

    missing = 0

    for scenario in charter:
        scenario_name = str(scenario.get("testScenario") or "").strip()
        for tc in scenario.get("testCases", []) or []:
            case_id = str(tc.get("id") or "").strip()
            if not case_id:
                continue
            steps = tc.get("steps") or []
            if _has_intent_steps(steps):
                continue

            missing += 1
            desc = str(tc.get("description") or "")
            intents, notes = _suggest_for_case(case_id, scenario_name, desc)

            suggestions.append(
                {
                    "case_id": case_id,
                    "scenario": scenario_name,
                    "suggested_steps": intents,
                    "notes": notes,
                }
            )

            lines.append(f"\n## {case_id}\n")
            lines.append(f"- Scenario: {scenario_name}\n")
            b = _bullets(desc)
            if b:
                lines.append("- verify (aus Charter):\n")
                for x in b:
                    lines.append(f"  - {x}\n")
            lines.append("- vorgeschlagene Intents (abstrakt):\n")
            for s in intents:
                extra = []
                for k in ["tab", "parameter", "value", "query", "min_results", "sections"]:
                    if k in s:
                        extra.append(f"{k}={s[k]}")
                if s.get("spec_required"):
                    extra.append("SPEC_REQUIRED")
                suffix = (" (" + ", ".join(extra) + ")") if extra else ""
                lines.append(f"  - {s['intent']}{suffix}\n")
            if notes:
                lines.append("- Notes:\n")
                for n in notes:
                    lines.append(f"  - {n}\n")

    lines.append("\n## Summary\n")
    lines.append(f"- Testfälle ohne intent-steps: {missing}\n")
    lines.append("- Nächster Schritt: Review + SPEC_REQUIRED beantworten; dann Intents schrittweise im Runner implementieren.\n")

    md_path.write_text("".join(lines), encoding="utf-8")
    latest_md.write_text("".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
