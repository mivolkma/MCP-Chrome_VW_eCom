#!/usr/bin/env python
"""Check Markdown relative links inside the repository.

- Scans *.md files.
- Validates that local link targets exist.
- Ignores http(s) links, mailto, anchors-only, and code blocks.

Exit code:
- 0: no missing links
- 1: missing links found

This tool is safe to run in CI or locally; it does not access network.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
CODE_FENCE_RE = re.compile(r"^\s*```")


@dataclass(frozen=True)
class MissingLink:
    md_file: Path
    target: str


def _iter_md_files(root: Path) -> list[Path]:
    return sorted([p for p in root.rglob("*.md") if p.is_file()])


def _strip_code_fences(text: str) -> str:
    """Remove fenced code blocks to avoid false-positive links."""
    lines = text.splitlines()
    in_fence = False
    kept: list[str] = []
    for line in lines:
        if CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    return "\n".join(kept)


def _is_ignored_target(t: str) -> bool:
    t = t.strip()
    return (
        t.startswith("http://")
        or t.startswith("https://")
        or t.startswith("mailto:")
        or t.startswith("#")
        or t.startswith("vscode://")
        or t.startswith("file://")
    )


def _normalize_target(t: str) -> str:
    t = t.strip()
    # Remove title part: (path "title")
    if " " in t and not t.startswith("<"):
        t = t.split(" ", 1)[0]
    # Remove anchor: path#section
    if "#" in t:
        t = t.split("#", 1)[0]
    # URL decode minimal (%20)
    t = t.replace("%20", " ")
    return t


def _target_exists(md_file: Path, target: str, repo_root: Path) -> bool:
    target = _normalize_target(target)
    if not target:
        return True

    # Absolute-from-repo-root style
    if target.startswith("/"):
        candidate = repo_root / target.lstrip("/")
    else:
        candidate = (md_file.parent / target)

    # If it points to a directory, accept if directory exists
    if candidate.exists():
        return True

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Markdown files for broken relative links")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repo root (default: .)")
    args = parser.parse_args()

    repo_root = args.root.resolve()
    missing: list[MissingLink] = []

    for md_file in _iter_md_files(repo_root):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        content = _strip_code_fences(content)
        for raw_target in LINK_RE.findall(content):
            if _is_ignored_target(raw_target):
                continue
            if not _target_exists(md_file, raw_target, repo_root):
                missing.append(MissingLink(md_file=md_file, target=_normalize_target(raw_target)))

    if not missing:
        print("OK: No broken relative Markdown links found.")
        return 0

    print("Broken relative Markdown links:")
    for item in missing:
        rel = item.md_file.relative_to(repo_root)
        print(f"- {rel}: {item.target}")

    print(f"\nFAIL: {len(missing)} broken link(s)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
