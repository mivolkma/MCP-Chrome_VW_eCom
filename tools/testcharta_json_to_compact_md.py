#!/usr/bin/env python
"""Convert the BTO testcharta JSON into a compact, human-readable Markdown checklist.

Defaults are set to git-available locations under prompts/testdata so agents can run
without relying on ignored results/**.
If prompts/testdata is missing, the script falls back to results/testdata.

No secrets are read or written.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_INPUT_CANDIDATES = [
    Path("prompts/testdata/BTO-testcharta.json"),
    Path("results/testdata/BTO-testcharta.json"),
]


def _pick_default_input() -> Path:
    for candidate in DEFAULT_INPUT_CANDIDATES:
        if candidate.exists():
            return candidate
    # Prefer prompts/ for new setups, even if file isn't there yet.
    return DEFAULT_INPUT_CANDIDATES[0]


def _clean(s: Any) -> str:
    if s is None:
        return ""
    return str(s).replace("\r\n", "\n").strip()


def _step_line(step: dict[str, Any]) -> str:
    action = _clean(step.get("action"))
    value = _clean(step.get("value"))
    field = _clean(step.get("field"))
    testid = _clean(step.get("data-testid"))

    parts: list[str] = []
    if action:
        parts.append(action)
    if field:
        parts.append(f"field={field}")
    if value:
        parts.append(f"value={value}")
    if testid:
        parts.append(f"testid={testid}")

    return " - ".join(parts) if parts else "(leer)"


def convert(input_path: Path, output_path: Path, skip_last: bool) -> None:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Expected top-level JSON array")

    scenarios = raw
    if skip_last and scenarios:
        scenarios_to_render = scenarios[:-1]
        skipped = scenarios[-1]
    else:
        scenarios_to_render = scenarios
        skipped = None

    lines: list[str] = []
    lines.append(f"# BTO Testcharta – kompakte Steps ({len(scenarios_to_render)} Szenarien)")
    lines.append("")
    lines.append(f"Quelle: {input_path.as_posix()}")
    lines.append("")
    lines.append("Hinweise:")
    lines.append("- Keine Secrets/Tokens in Logs oder Dateien schreiben.")
    lines.append("- Bekannter Chrome-Dialog: Bei Domain-Endung `.eu` Credentials erneut eingeben und fortfahren; bei `.io` Dialog schließen.")
    lines.append("- E-Mail für Tests: test@test.de")
    if skip_last:
        lines.append("- Letztes Szenario wird übersprungen (derzeit nur via VPN erreichbar).")
    lines.append("")

    for idx, scenario in enumerate(scenarios_to_render, start=1):
        if not isinstance(scenario, dict):
            continue
        title = _clean(scenario.get("testScenario")) or f"Szenario {idx}"
        lines.append(f"## {idx}. {title}")

        desc = _clean(scenario.get("description"))
        if desc:
            lines.append("")
            lines.append("**Beschreibung**")
            lines.append(desc)

        test_cases = scenario.get("testCases")
        if isinstance(test_cases, list) and test_cases:
            lines.append("")
            lines.append("**Testcases**")
            for tc in test_cases:
                if not isinstance(tc, dict):
                    continue
                tc_id = _clean(tc.get("id")) or "(ohne id)"
                tc_desc = _clean(tc.get("description"))
                lines.append(f"- {tc_id}: {tc_desc.splitlines()[0] if tc_desc else ''}".rstrip())

                steps = tc.get("steps")
                if isinstance(steps, list) and steps:
                    for step in steps:
                        if isinstance(step, dict):
                            lines.append(f"  - {_step_line(step)}")

        negative = scenario.get("negativeTests")
        if isinstance(negative, list) and negative:
            lines.append("")
            lines.append("**Negative Tests (Auszug)**")
            for nt in negative[:5]:
                if not isinstance(nt, dict):
                    continue
                nt_desc = _clean(nt.get("description"))
                lines.append(f"- {nt_desc}" if nt_desc else "- (ohne Beschreibung)")

        lines.append("")

    if skipped is not None and isinstance(skipped, dict):
        lines.append("## Übersprungen (VPN)")
        title = _clean(skipped.get("testScenario")) or "(ohne Titel)"
        lines.append(f"- {title}")
        desc = _clean(skipped.get("description"))
        if desc:
            lines.append(f"  - {desc.splitlines()[0]}")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert BTO testcharta JSON to compact Markdown")
    parser.add_argument(
        "--input",
        type=Path,
        default=_pick_default_input(),
        help=(
            "Input JSON path (default: prompts/testdata/BTO-testcharta.json; "
            "falls nicht vorhanden: results/testdata/BTO-testcharta.json)"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("prompts/testdata/BTO-testcharta_compact.md"),
        help="Output Markdown path (default: prompts/testdata/BTO-testcharta_compact.md)",
    )
    parser.add_argument(
        "--skip-last",
        action="store_true",
        help="Skip the last scenario (e.g., VPN-only)",
    )

    args = parser.parse_args()
    convert(args.input, args.output, skip_last=args.skip_last)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
