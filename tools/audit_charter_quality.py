import argparse
import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class BulletAssessment:
    bullet: str
    status: str  # OK | PARTIAL | GAP | SPEC_REQUIRED
    reason: str
    mapped_intents: list[str]


# Heuristic intent catalog (static: what our runner currently supports).
KNOWN_INTENTS: set[str] = {
    "start_checkout",
    "assert_checkout_loaded",
    "assert_tab_slider_present",
    "assert_price_box_present",
    "assert_sticky_bar_present",
}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _bullets_from_text(text: str) -> list[str]:
    bullets: list[str] = []
    for line in (text or "").splitlines():
        line = line.strip()
        if line.startswith("-"):
            b = line.strip("- ").strip()
            if b:
                bullets.append(b)
    return bullets


def _intents_from_steps(steps: Iterable[dict]) -> list[str]:
    intents: list[str] = []
    for s in steps or []:
        if str(s.get("action") or "").strip().lower() == "intent":
            i = str(s.get("intent") or "").strip()
            if i:
                intents.append(i)
    return intents


def _has_intent(intents: list[str], name: str) -> bool:
    return any(i == name for i in intents)


def _spec_required(reason: str, intents: list[str] | None = None) -> BulletAssessment:
    return BulletAssessment(
        bullet="",
        status="SPEC_REQUIRED",
        reason=reason,
        mapped_intents=intents or [],
    )


def assess_bullet(bullet: str, intents: list[str]) -> BulletAssessment:
    b = (bullet or "").strip()
    bl = b.lower()

    mapped: list[str] = []

    def has(i: str) -> bool:
        return _has_intent(intents, i)

    # Multi-component bullets (common in OH-eCom-BTO-02): evaluate components separately.
    # Important: "Next Step CTA" is NOT the "eCom CTA".
    components: list[str] = []
    if "tab slider" in bl or "tabs" in bl:
        components.append("tab_slider")
    if "price box" in bl:
        components.append("price_box")
    if "sticky bar" in bl or "next step cta" in bl or "next step" in bl:
        components.append("sticky_bar")
    if "disclaimer" in bl:
        components.append("disclaimers")
    if "content of the current" in bl and "journey step" in bl:
        components.append("journey_step_content")

    if len(components) >= 2:
        # Determine intent coverage for the components.
        covered: list[str] = []
        gaps: list[str] = []

        if "tab_slider" in components:
            mapped.append("assert_tab_slider_present")
            (covered if has("assert_tab_slider_present") else gaps).append("tab slider")
        if "price_box" in components:
            mapped.append("assert_price_box_present")
            (covered if has("assert_price_box_present") else gaps).append("price box")
        if "sticky_bar" in components:
            mapped.append("assert_sticky_bar_present")
            (covered if has("assert_sticky_bar_present") else gaps).append("sticky bar / Next Step CTA")
        if "disclaimers" in components:
            gaps.append("disclaimers")
        if "journey_step_content" in components:
            gaps.append("journey step content")

        if covered and not gaps:
            return BulletAssessment(b, "PARTIAL", "Mehrere UI-Komponenten: Presence-Checks sind vorhanden; Semantik/Inhalt nicht vollständig autom. belegt.", mapped)
        if covered and gaps:
            return BulletAssessment(
                b,
                "PARTIAL",
                "Abgedeckt: " + ", ".join(covered) + ". Lücken: " + ", ".join(gaps) + ".",
                mapped,
            )
        return BulletAssessment(b, "GAP", "Keine passenden Intents für die genannten UI-Komponenten im TestCase.", mapped)

    # CTA / journey start (must be the eCom CTA, not the Next Step CTA)
    if any(k in bl for k in ["ecom cta", "starting the ecommerce journey", "starts the corresponding ecommerce journey"]):
        mapped.append("start_checkout")
        if has("start_checkout"):
            return BulletAssessment(b, "PARTIAL", "Intent vorhanden (start_checkout); Ergebnis/Navigation hängt von Variante ab.", mapped)
        return BulletAssessment(b, "GAP", "Kein start_checkout Intent im TestCase (Hinweis: evtl. in anderem TestCase abgedeckt).", mapped)

    if "opens a new page" in bl and "ecom cta" in bl:
        mapped.append("start_checkout")
        if has("start_checkout"):
            return BulletAssessment(b, "PARTIAL", "Intent vorhanden (start_checkout); Navigation wird best-effort geprüft.", mapped)
        return BulletAssessment(b, "GAP", "Kein start_checkout Intent im TestCase (Hinweis: evtl. in anderem TestCase abgedeckt).", mapped)

    # Price box
    if "price box" in bl:
        mapped.append("assert_price_box_present")
        if has("assert_price_box_present"):
            if any(k in bl for k in ["correct information", "passed on", "total price", "car's name", "selected financing parameters"]):
                return BulletAssessment(
                    b,
                    "SPEC_REQUIRED",
                    "Erfordert definierte, maschinenprüfbare Erwartungswerte/Quelle (z.B. API/DOM-Felder).",
                    mapped,
                )
            return BulletAssessment(b, "PARTIAL", "Presence wird geprüft; inhaltliche Korrektheit ist noch nicht autom. belegt.", mapped)
        return BulletAssessment(b, "GAP", "Kein assert_price_box_present Intent im TestCase.", mapped)

    # Sticky bar / Next Step
    if any(k in bl for k in ["sticky bar", "next step cta", "next step", "weiter", "nächster schritt"]):
        mapped.append("assert_sticky_bar_present")
        if has("assert_sticky_bar_present"):
            return BulletAssessment(b, "PARTIAL", "Presence wird geprüft; Verhalten (sticky beim Scroll) ist noch nicht abgedeckt.", mapped)
        return BulletAssessment(b, "GAP", "Kein assert_sticky_bar_present Intent im TestCase.", mapped)

    # Tab slider
    if any(k in bl for k in ["tab slider", "tabs", "sliding", "arrows", "arrow"]):
        mapped.append("assert_tab_slider_present")
        if not has("assert_tab_slider_present"):
            return BulletAssessment(b, "GAP", "Kein assert_tab_slider_present Intent im TestCase.", mapped)

        if "many" in bl or "cover" in bl:
            return BulletAssessment(
                b,
                "SPEC_REQUIRED",
                "Charter-Text ist ohne Definition nicht messbar ('many tabs' / 'cover all journey steps').",
                mapped,
            )

        if "deactiv" in bl or "deactivated" in bl:
            return BulletAssessment(
                b,
                "PARTIAL",
                "Best-effort Disabled-Erkennung möglich, aber Varianten/ARIA können abweichen.",
                mapped,
            )

        if "arrow" in bl or "arrows" in bl or "sliding" in bl:
            return BulletAssessment(
                b,
                "PARTIAL",
                "Arrow-Funktion kann bei Overflow geprüft werden (inkl. Viewport-Probing).",
                mapped,
            )

        return BulletAssessment(b, "PARTIAL", "Tab-Slider Presence wird geprüft; Semantik ggf. unklar.", mapped)

    # Disclaimers
    if "disclaimer" in bl:
        return BulletAssessment(b, "GAP", "Disclaimers werden aktuell nicht als eigener deterministischer Check geprüft.", [])

    # Checkout/eCom page loaded (generic, after specific UI components)
    if any(k in bl for k in ["ecom page", "starts with the personal data tab", "page displays"]):
        mapped.append("assert_checkout_loaded")
        if has("assert_checkout_loaded"):
            if "starts with" in bl and "personal data" in bl:
                return BulletAssessment(
                    b,
                    "SPEC_REQUIRED",
                    "Erfordert maschinenprüfbare Definition, wie 'personal data tab' eindeutig erkannt wird (Selector/Label/URL/State).",
                    mapped,
                )
            return BulletAssessment(b, "PARTIAL", "Presence/Anchor-Prüfung möglich; Semantik nicht vollständig belegt.", mapped)
        return BulletAssessment(b, "GAP", "Kein assert_checkout_loaded Intent im TestCase.", mapped)

    # Generic fallback
    return BulletAssessment(b, "GAP", "Keine Zuordnung zu einem implementierten Intent; vermutlich Test-Gap.", [])


def _md_escape(s: str) -> str:
    return (s or "").replace("\r", "").replace("\n", " ")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--charter",
        default=str(Path("prompts/testdata/bto/v1.0/charter.json")),
        help="Path to charter.json",
    )
    ap.add_argument("--output", default="", help="Output markdown path")
    args = ap.parse_args()

    charter_path = Path(args.charter)
    charter = _load_json(charter_path)

    ts = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = Path("results/bto-checkout/reports") / f"charter_quality_audit_{ts}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    counts = {"OK": 0, "PARTIAL": 0, "GAP": 0, "SPEC_REQUIRED": 0}
    total_bullets = 0
    total_cases = 0
    cases_with_intents = 0
    cases_without_intents: list[str] = []

    lines: list[str] = []
    lines.append(f"# Charter Quality Audit\n")
    lines.append(f"- Zeitpunkt: {dt.datetime.now().isoformat(timespec='seconds')}\n")
    lines.append(f"- Charter: {charter_path.as_posix()}\n")
    lines.append(f"- Bekannte Intents im Runner: {', '.join(sorted(KNOWN_INTENTS))}\n")
    lines.append("\n## Summary\n")

    scenario_sections: list[str] = []

    for scenario in charter:
        scenario_name = str(scenario.get("testScenario") or "").strip()
        for tc in scenario.get("testCases", []) or []:
            case_id = str(tc.get("id") or "").strip()
            if not case_id:
                continue

            total_cases += 1

            desc = str(tc.get("description") or "")
            bullets = _bullets_from_text(desc)
            intents = _intents_from_steps(tc.get("steps") or [])
            if intents:
                cases_with_intents += 1
            else:
                cases_without_intents.append(case_id)

            section: list[str] = []
            section.append(f"\n## {case_id} — {_md_escape(scenario_name)}\n")
            if intents:
                section.append(f"- Intents: {', '.join(intents)}\n")
            else:
                section.append(f"- Intents: (keine)\n")

            if not bullets:
                section.append("- Charter-Bullets: (keine im Description-Text gefunden)\n")
                continue

            section.append("\n| Bullet | Status | Begründung |\n")
            section.append("|---|---|---|\n")

            for b in bullets:
                total_bullets += 1
                a = assess_bullet(b, intents)
                counts[a.status] = counts.get(a.status, 0) + 1
                section.append(f"| {_md_escape(b)} | {a.status} | {_md_escape(a.reason)} |\n")

            # Negative tests are currently not expressed as intents in our runner.
            neg = scenario.get("negativeTests") or []
            if isinstance(neg, list) and neg:
                section.append("\n**Negative Tests (Charter):**\n")
                section.append("- Status: GAP (nicht als Intents modelliert; aktuell nicht automatisiert abgedeckt)\n")

            # Device matrix: our runner runs desktop + some viewport probing, but not full matrix.
            dm = scenario.get("deviceMatrix") or []
            if isinstance(dm, list) and dm:
                section.append("\n**Device Matrix (Charter):**\n")
                section.append(f"- Erwartet: {', '.join(map(str, dm))}\n")
                section.append("- Status: PARTIAL (Runner nutzt Desktop; einige Checks können Viewport-Probing machen, aber kein kompletter Matrix-Run)\n")

            scenario_sections.append("".join(section))

    lines.append(
        f"- Bullets gesamt: {total_bullets}\n"
        f"- TestCases gesamt: {total_cases}\n"
        f"- TestCases mit Intents: {cases_with_intents}\n"
        f"- TestCases ohne Intents: {len(cases_without_intents)}\n"
        f"- OK: {counts.get('OK', 0)}\n"
        f"- PARTIAL: {counts.get('PARTIAL', 0)}\n"
        f"- SPEC_REQUIRED: {counts.get('SPEC_REQUIRED', 0)}\n"
        f"- GAP: {counts.get('GAP', 0)}\n"
    )

    if cases_without_intents:
        lines.append("\n## TestCases ohne Automation (keine Intents)\n")
        lines.append(
            "Diese TestCases enthalten in charter.json keine `intent`-Steps und werden vom Runner daher nicht sinnvoll automatisiert.\n"
        )
        for cid in cases_without_intents:
            lines.append(f"- {cid}\n")

    lines.append("\n## Top Findings (konservativ)\n")
    lines.append("- Viele Charter-Punkte sind semantisch (Inhalt/Korrektheit) und brauchen SPEC_REQUIRED-Definitionen oder neue Atomic-Checks.\n")
    lines.append("- Negative Tests sind im Charter vorhanden, aber aktuell nicht als Runner-Intents abgebildet (Test-Gap).\n")
    lines.append("- Device-Matrix wird nicht vollständig automatisiert durchlaufen (aktuell Partial).\n")

    lines.extend(scenario_sections)

    out_path.write_text("".join(lines), encoding="utf-8")

    # Write/update a stable "latest" file as well.
    latest_path = out_path.parent / "latest_charter_quality_audit.md"
    latest_path.write_text("".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
