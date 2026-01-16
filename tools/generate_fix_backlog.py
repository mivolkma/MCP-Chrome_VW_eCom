import argparse
import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SpecQuestion:
    area: str
    question: str
    case_ids: list[str]


def _detect_charter_language(charter) -> str:
    """Best-effort detection: if verify bullets look English → 'en', else 'de'."""
    verify_lines: list[str] = []
    for scenario in charter or []:
        for tc in scenario.get("testCases", []) or []:
            for b in _bullets(str(tc.get("description") or "")):
                verify_lines.append(b)

    sample = " ".join(verify_lines).lower()
    english_markers = [
        " the ",
        " a ",
        " an ",
        " is ",
        " are ",
        " when ",
        " displayed ",
        " should ",
        " opens ",
        " starts with ",
        " price box ",
        " sticky ",
        " disclaimer ",
    ]
    hits = sum(1 for m in english_markers if m in f" {sample} ")
    return "en" if hits >= 2 else "de"


def _t(lang: str, key: str) -> str:
    tr = {
        "de": {
            "title": "Fix-Backlog & SPEC_REQUIRED Fragen (aus Charter)",
            "timestamp": "Zeitpunkt",
            "charter": "Charter",
            "howto_title": "Wie du das beantwortest (kurz)",
            "howto_1": "- Ziel ist eine **deterministische Regel**, nicht ein Bauchgefühl.",
            "howto_2": "- Wenn du es nicht deterministisch definieren kannst: schreibe genau das in 'Kurzdefinition' (bleibt SPEC_REQUIRED).",
            "howto_3": "- Selektoren/TestIDs sind hilfreich, aber eine klare Regel ist wichtiger.",
            "p0_quality": "P0 – Struktur/Qualität (sofort)",
            "total_cases": "TestCases gesamt",
            "cases_with_intents": "TestCases mit Intents",
            "cases_without_intents": "TestCases ohne Intents",
            "recommendation": "- Empfehlung: Charter/Runner so ausbauen, dass jeder TestCase mindestens 1–n Intents hat (atomare Checks), sonst bleibt es manuell/unklar.",
            "p0_spec": "P0 – SPEC_REQUIRED Fragen (bitte beantworten)",
            "none_found": "- (Keine SPEC_REQUIRED-Patterns gefunden – ggf. Heuristik erweitern.)",
            "case": "Testfall",
            "answer_header": "Antwort (bitte ausfüllen)",
            "shortdef": "Kurzdefinition (1 Satz)",
            "method": "Prüfmethode (wie beweisen wir das?)",
            "selectors": "Selektoren/TestIDs/ARIA (falls bekannt)",
            "edge": "Edge-Cases/Varianten (Viewport/Locale/etc.)",
            "p1_gaps": "P1 – TestCases ohne Intents (Automation-Lücken)",
            "p1_gaps_desc": "Diese Cases sind in charter.json aktuell ohne `intent`-Steps und daher im Runner nicht abgedeckt:",
            "p1_negative": "P1 – Negative Tests",
            "p1_negative_1": "- Charter enthält negative Tests (z.B. leere Pflichtfelder, invalid email), aber sie sind nicht als Intents modelliert.",
            "p1_negative_2": "- Vorschlag: eigene Intents für Form-Validation/Errors + erwartete Error-Selectors/Texte (SPEC_REQUIRED falls unklar).",
            "p2_device": "P2 – Device Matrix",
            "p2_device_1": "- Charter erwartet mehrere Devices; aktuell gibt es nur Desktop + punktuelles Viewport-Probing in einzelnen Checks.",
            "p2_device_2": "- Vorschlag: optionaler Matrix-Run (Desktop/Tablet/Mobile) als orchestrierter Modus.",
        },
        "en": {
            "title": "Fix backlog & SPEC_REQUIRED questions (from charter)",
            "timestamp": "Timestamp",
            "charter": "Charter",
            "howto_title": "How to answer (short)",
            "howto_1": "- Goal is a **deterministic rule**, not a gut feeling.",
            "howto_2": "- If you cannot define it deterministically: write that explicitly in 'Short definition' (remains SPEC_REQUIRED).",
            "howto_3": "- Selectors/test IDs help, but a clear rule is more important.",
            "p0_quality": "P0 – Structure/quality (now)",
            "total_cases": "Total test cases",
            "cases_with_intents": "Test cases with intents",
            "cases_without_intents": "Test cases without intents",
            "recommendation": "- Recommendation: extend charter/runner so each test case has 1–n intents (atomic checks); otherwise it stays manual/unclear.",
            "p0_spec": "P0 – SPEC_REQUIRED questions (please answer)",
            "none_found": "- (No SPEC_REQUIRED patterns found – consider extending heuristics.)",
            "case": "Test case",
            "answer_header": "Answer (please fill)",
            "shortdef": "Short definition (1 sentence)",
            "method": "Test method (how do we prove it?)",
            "selectors": "Selectors/test IDs/ARIA (if known)",
            "edge": "Edge cases/variants (viewport/locale/etc.)",
            "p1_gaps": "P1 – Test cases without intents (automation gaps)",
            "p1_gaps_desc": "These cases currently have no `intent` steps in charter.json and are therefore not covered by the runner:",
            "p1_negative": "P1 – Negative tests",
            "p1_negative_1": "- Charter contains negative tests (e.g. empty required fields, invalid email), but they are not modeled as intents.",
            "p1_negative_2": "- Suggestion: add dedicated intents for form validation/errors + expected selectors/texts (SPEC_REQUIRED if unclear).",
            "p2_device": "P2 – Device matrix",
            "p2_device_1": "- Charter expects multiple devices; currently there is only Desktop + occasional viewport probing in a few checks.",
            "p2_device_2": "- Suggestion: optional matrix run (Desktop/Tablet/Mobile) as an orchestrated mode.",
        },
    }
    return tr.get(lang, tr["en"]).get(key, key)


def _q(lang: str, key: str) -> str:
    qs = {
        "de": {
            "dealer_results": "Wie definierst du deterministisch 'many corresponding results'? (Mindestanzahl, ggf. Limit, Sortierung, was ist ein 'corresponding' Treffer)",
            "tab_slider": "Wie definierst du deterministisch 'many tabs' und 'cover all eCom journey steps'? (z.B. tab labels == step list, Mindestanzahl, Mapping-Regeln, Umgang mit hidden/disabled steps)",
            "personal_data": "Wie erkennt der Test deterministisch den 'personal data tab'? (Selector/TestId/Label/aria-selected, Sprache/Locale, Fallback-Regeln)",
            "price_box": "Welche Felder müssen in der Preisbox exakt stimmen und gegen welche Quelle vergleichen wir sie? (DOM-Felder, API-Responses, Toleranzen/Format)",
            "sticky_scroll": "Wie definierst du 'sticky bar sticks while scrolling until footer is accessed'? (Scroll-Schwellen, Footer-Erkennung, erwartetes Verhalten beim Erreichen des Footers)",
            "step_completed": "Was bedeutet 'current step is completed' pro Step und wie muss sich die Navigation verhalten? (Completion-Kriterien, erwarteter Step-Index/URL/State)",
            "disclaimer": "Welche Disclaimer-Referenzen/Texte sind erwartbar (genauer Wortlaut/IDs), und wie prüfen wir sie robust? (Anzahl, Position, Summary-Step CO2-Disclaimer)",
        },
        "en": {
            "dealer_results": "How do you define 'many corresponding results' deterministically? (min count, optional limit, sorting, what is a 'corresponding' result)",
            "tab_slider": "How do you define 'many tabs' and 'cover all eCom journey steps' deterministically? (e.g. tab labels == step list, min count, mapping rules, handling hidden/disabled steps)",
            "personal_data": "How does the test detect the 'personal data tab' deterministically? (selector/testId/label/aria-selected, locale/language, fallback rules)",
            "price_box": "Which fields in the price box must match exactly and against which source do we compare? (DOM fields, API responses, tolerances/format)",
            "sticky_scroll": "How do you define 'sticky bar sticks while scrolling until footer is accessed'? (scroll thresholds, footer detection, expected behavior when footer is reached)",
            "step_completed": "What does 'current step is completed' mean per step and how must navigation behave? (completion criteria, expected step index/url/state)",
            "disclaimer": "Which disclaimer references/texts are expected (exact wording/ids), and how do we validate them robustly? (count, position, summary-step CO2 disclaimer)",
        },
    }
    return qs.get(lang, qs["en"]).get(key, key)


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _bullets(text: str) -> list[str]:
    out: list[str] = []
    for line in (text or "").splitlines():
        line = line.strip()
        if line.startswith("-"):
            b = line.strip("- ").strip()
            if b:
                out.append(b)
    return out


def _intents_from_steps(steps) -> list[str]:
    intents: list[str] = []
    for s in steps or []:
        if str(s.get("action") or "").strip().lower() == "intent":
            i = str(s.get("intent") or "").strip()
            if i:
                intents.append(i)
    return intents


def _guess_area(b: str, lang: str) -> str:
    bl = b.lower()
    if "postal" in bl or "cities" in bl or "corresponding results" in bl:
        return "Dealer-Suche / Results" if lang == "de" else "Dealer search / results"
    if "tab slider" in bl or "arrows" in bl or "tabs" in bl:
        return "Tab-Slider"
    if "price box" in bl:
        return "Preisbox" if lang == "de" else "Price box"
    if "sticky bar" in bl or "next step" in bl:
        return "Sticky Bar / Next Step"
    if "disclaimer" in bl or "co2" in bl:
        return "Disclaimer"
    if "personal data" in bl:
        return "Personal Data Tab"
    if "financing" in bl or "offer" in bl or "leasing" in bl:
        return "Financing / Offer"
    if "dealer" in bl or "pickup" in bl:
        return "Dealer / Pickup"
    if "consent" in bl:
        return "Consents"
    return "Sonstiges" if lang == "de" else "Other"


def _needs_spec(b: str) -> bool:
    bl = b.lower()
    return any(
        k in bl
        for k in [
            "many",
            "cover all",
            "correct information",
            "passed on",
            "sticks",
            "while scrolling",
            "always leads",
            "corresponding disclaimer",
            "co2",
            "starts with",
            # German-ish markers (in case the charter is DE)
            "viele",
            "deckt",
            "korrekt",
            "übergeben",
            "klebt",
            "beim scroll",
            "führt",
            "haftungsausschluss",
            "beginnt",
        ]
    ) or ("total price" in bl and "price box" in bl)


def _answer_template(area: str, lang: str) -> list[str]:
    common = [
        f"  - {_t(lang, 'answer_header')}:",
        f"    - {_t(lang, 'shortdef')}: <TODO>",
        f"    - {_t(lang, 'method')}: <TODO>",
        f"    - {_t(lang, 'selectors')}: <TODO>",
        f"    - {_t(lang, 'edge')}: <TODO>",
    ]

    if area == "Tab-Slider":
        if lang == "de":
            return common + [
                "    - Erwartung zu 'many': <TODO z.B. >= 6 Tabs oder >= 8 Tabs>",
                "    - Erwartung zu 'cover all steps': <TODO z.B. Set(TabLabels) == Set(StepNames)>",
            ]
        return common + [
            "    - Expectation for 'many': <TODO e.g. >= 6 tabs or >= 8 tabs>",
            "    - Expectation for 'cover all steps': <TODO e.g. Set(TabLabels) == Set(StepNames)>",
        ]
    if area in ("Preisbox", "Price box"):
        if lang == "de":
            return common + [
                "    - Pflichtfelder (Name, Rate, Total, km, Laufzeit, Anzahlung): <TODO>",
                "    - Quelle der Wahrheit (DOM vs API) + Mapping: <TODO>",
                "    - Toleranzen/Format (Währung, Dezimal, Tausender, Rundung): <TODO>",
            ]
        return common + [
            "    - Required fields (name, rate, total, km, term, down payment): <TODO>",
            "    - Source of truth (DOM vs API) + mapping: <TODO>",
            "    - Tolerances/format (currency, decimals, thousands, rounding): <TODO>",
        ]
    if area == "Sticky Bar / Next Step":
        if lang == "de":
            return common + [
                "    - Definition 'sticky': <TODO z.B. CTA bleibt sichtbar + am Viewport-Bottom (BoundingBox)>",
                "    - Definition 'Footer accessed': <TODO z.B. footer im Viewport sichtbar/Intersecting>",
                "    - Definition 'Step completed': <TODO z.B. required fields valid, button enabled, step-state>",
            ]
        return common + [
            "    - Definition 'sticky': <TODO e.g. CTA stays visible + at viewport bottom (bounding box)>",
            "    - Definition 'footer accessed': <TODO e.g. footer is visible/intersecting in viewport>",
            "    - Definition 'step completed': <TODO e.g. required fields valid, button enabled, step-state>",
        ]
    if area == "Disclaimer":
        if lang == "de":
            return common + [
                "    - Wie viele Disclaimer-Refs? Wo genau (neben Total Price, neben Rate): <TODO>",
                "    - Wie wird Ref→Text gemappt (ID/Anchor/aria-describedby)? <TODO>",
                "    - Erwartung im Summary-Step (CO2-Class): <TODO>",
            ]
        return common + [
            "    - How many disclaimer refs? Where exactly (next to total price, next to rate): <TODO>",
            "    - How is ref→text mapped (id/anchor/aria-describedby)? <TODO>",
            "    - Expectation in summary step (CO2 class): <TODO>",
        ]
    if area == "Personal Data Tab":
        if lang == "de":
            return common + [
                "    - Erkennung 'starts with personal data tab' (active tab label/aria-selected): <TODO>",
            ]
        return common + [
            "    - Detection of 'starts with personal data tab' (active tab label/aria-selected): <TODO>",
        ]
    if area in ("Dealer-Suche / Results", "Dealer search / results"):
        if lang == "de":
            return common + [
                "    - Definition 'many corresponding results': <TODO z.B. >= 3 Treffer; max N; Sortierung>",
                "    - Input-Daten (Beispiel city/PLZ): <TODO>",
            ]
        return common + [
            "    - Definition of 'many corresponding results': <TODO e.g. >= 3 results; max N; sorting>",
            "    - Input data (example city/postal): <TODO>",
        ]

    return common


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
    ap.add_argument(
        "--lang",
        choices=["de", "en", "auto"],
        default="auto",
        help="Language for questions/templates. Use 'auto' to detect from charter.",
    )
    args = ap.parse_args()

    charter_path = Path(args.charter)
    charter = _load_json(charter_path)

    lang = str(args.lang).strip().lower()
    if lang == "auto":
        lang = _detect_charter_language(charter)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    ts = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = outdir / f"fix_backlog_{ts}.md"
    latest_path = outdir / "latest_fix_backlog.md"

    total_cases = 0
    cases_with_intents = 0
    no_intent_cases: list[tuple[str, str]] = []  # (case_id, scenario)

    spec_map: dict[tuple[str, str], dict[str, list[str]]] = {}  # (area, question) -> {case_id: [verify_bullets]}

    def add_spec(area: str, question: str, case_id: str, verify_bullet: str):
        per_case = spec_map.setdefault((area, question), {})
        per_case.setdefault(case_id, [])
        if verify_bullet and verify_bullet not in per_case[case_id]:
            per_case[case_id].append(verify_bullet)

    # Walk charter
    for scenario in charter:
        scenario_name = str(scenario.get("testScenario") or "").strip()
        for tc in scenario.get("testCases", []) or []:
            case_id = str(tc.get("id") or "").strip()
            if not case_id:
                continue
            total_cases += 1

            intents = _intents_from_steps(tc.get("steps") or [])
            if intents:
                cases_with_intents += 1
            else:
                no_intent_cases.append((case_id, scenario_name))

            for b in _bullets(str(tc.get("description") or "")):
                if not _needs_spec(b):
                    continue
                area = _guess_area(b, lang)
                bl = b.lower()

                if "many" in bl or "cover all" in bl:
                    if "corresponding results" in bl or "postal" in bl or "cities" in bl:
                        add_spec(
                            "Dealer-Suche / Results" if lang == "de" else "Dealer search / results",
                            _q(lang, "dealer_results"),
                            case_id,
                            b,
                        )
                        continue
                    add_spec(
                        area,
                        _q(lang, "tab_slider"),
                        case_id,
                        b,
                    )
                if "starts with" in bl and "personal data" in bl:
                    add_spec(
                        "Personal Data Tab",
                        _q(lang, "personal_data"),
                        case_id,
                        b,
                    )
                if "correct information" in bl or "passed on" in bl or ("price box" in bl and "total price" in bl):
                    add_spec(
                        "Preisbox" if lang == "de" else "Price box",
                        _q(lang, "price_box"),
                        case_id,
                        b,
                    )
                if "sticks" in bl or "while scrolling" in bl:
                    add_spec(
                        "Sticky Bar / Next Step",
                        _q(lang, "sticky_scroll"),
                        case_id,
                        b,
                    )
                if "always leads" in bl or ("next step" in bl and "completed" in bl):
                    add_spec(
                        "Sticky Bar / Next Step",
                        _q(lang, "step_completed"),
                        case_id,
                        b,
                    )
                if "disclaimer" in bl or "co2" in bl:
                    add_spec(
                        "Disclaimer",
                        _q(lang, "disclaimer"),
                        case_id,
                        b,
                    )

    # Compose report
    lines: list[str] = []
    lines.append(f"# {_t(lang, 'title')}\n")
    lines.append(f"- {_t(lang, 'timestamp')}: {dt.datetime.now().isoformat(timespec='seconds')}\n")
    lines.append(f"- {_t(lang, 'charter')}: {charter_path.as_posix()}\n")
    lines.append(f"- Language: {lang}\n")

    lines.append(f"\n## {_t(lang, 'howto_title')}\n")
    lines.append(_t(lang, "howto_1") + "\n")
    lines.append(_t(lang, "howto_2") + "\n")
    lines.append(_t(lang, "howto_3") + "\n")

    lines.append(f"\n## {_t(lang, 'p0_quality')}\n")
    lines.append(f"- {_t(lang, 'total_cases')}: {total_cases}\n")
    lines.append(f"- {_t(lang, 'cases_with_intents')}: {cases_with_intents}\n")
    lines.append(f"- {_t(lang, 'cases_without_intents')}: {len(no_intent_cases)}\n")
    lines.append(_t(lang, "recommendation") + "\n")

    lines.append(f"\n## {_t(lang, 'p0_spec')}\n")
    if not spec_map:
        lines.append(_t(lang, "none_found") + "\n")
    else:
        # stable order
        for (area, q), case_map in sorted(spec_map.items(), key=lambda x: (x[0][0], x[0][1])):
            lines.append(f"- [{area}] {q}\n")
            for i, (cid, verify_bullets) in enumerate(sorted(case_map.items(), key=lambda x: x[0]), start=1):
                lines.append(f"  - {_t(lang, 'case')} {i}: {cid}\n")
                lines.append("    verify:\n")
                for vb in verify_bullets:
                    lines.append(f"    - {vb}\n")
            for tline in _answer_template(area, lang):
                lines.append(tline + "\n")

    lines.append(f"\n## {_t(lang, 'p1_gaps')}\n")
    lines.append(_t(lang, "p1_gaps_desc") + "\n")
    for cid, scen in sorted(no_intent_cases, key=lambda x: x[0]):
        lines.append(f"- {cid}: {scen}\n")

    lines.append(f"\n## {_t(lang, 'p1_negative')}\n")
    lines.append(_t(lang, "p1_negative_1") + "\n")
    lines.append(_t(lang, "p1_negative_2") + "\n")

    lines.append(f"\n## {_t(lang, 'p2_device')}\n")
    lines.append(_t(lang, "p2_device_1") + "\n")
    lines.append(_t(lang, "p2_device_2") + "\n")

    out_path.write_text("".join(lines), encoding="utf-8")
    latest_path.write_text("".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
