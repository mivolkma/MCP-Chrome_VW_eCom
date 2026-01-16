import argparse
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup


@dataclass
class BulletStatus:
    case_id: str
    text: str
    status: str


def _collect_bullets(report_path: Path) -> list[BulletStatus]:
    soup = BeautifulSoup(report_path.read_text(encoding="utf-8"), "html.parser")
    out: list[BulletStatus] = []

    # Each test case has <h3 id="case-<ID>">, followed by a <div> containing the checklist.
    for h3 in soup.find_all("h3"):
        hid = h3.get("id") or ""
        if not hid.startswith("case-"):
            continue
        case_id = hid.replace("case-", "", 1)
        container = h3.find_next("div")
        if not container:
            continue
        ul = container.find("ul", class_="checklist")
        if not ul:
            continue
        for li in ul.find_all("li"):
            icon = li.find("span", class_="status-icon")
            spans = li.find_all("span")
            if not icon or len(spans) < 2:
                continue
            text = (spans[1].get_text(" ", strip=True) or "").strip()
            status = (icon.get("data-status") or "unknown").strip().lower()
            out.append(BulletStatus(case_id=case_id, text=text, status=status))

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Supervisor for BTO runs: enforces keep-it-green by gating on atomic checklist statuses.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--strict", action="store_true", help="Fail the run if any bullet is not pass (warn/unknown/fail).")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    report_path = run_dir / "BTO_Test_Report_v1.0.html"
    if not report_path.exists():
        raise SystemExit(f"Report not found: {report_path}")

    bullets = _collect_bullets(report_path)
    totals = {"pass": 0, "warn": 0, "fail": 0, "unknown": 0}
    for b in bullets:
        totals[b.status] = totals.get(b.status, 0) + 1

    lines: list[str] = []
    lines.append("# Supervisor Summary")
    lines.append("")
    lines.append(f"- Run dir: {run_dir.as_posix()}")
    lines.append(f"- Report: {report_path.name}")
    lines.append("")
    lines.append("## Atomic Checklist Totals")
    lines.append("")
    lines.append(f"- pass: {totals.get('pass',0)}")
    lines.append(f"- warn: {totals.get('warn',0)}")
    lines.append(f"- fail: {totals.get('fail',0)}")
    lines.append(f"- unknown: {totals.get('unknown',0)}")
    lines.append("")

    offenders = [b for b in bullets if b.status != "pass"]
    if offenders:
        lines.append("## Offenders (needs action)")
        lines.append("")
        for b in offenders[:30]:
            lines.append(f"- {b.case_id}: [{b.status}] {b.text}")
        if len(offenders) > 30:
            lines.append(f"- … plus {len(offenders)-30} more")
        lines.append("")

    summary_path = run_dir / "supervisor_summary.md"
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Quality gate
    if args.strict and offenders:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
