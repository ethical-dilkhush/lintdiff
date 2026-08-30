"""
lintdiff — show only changed lint rules between two lint reports.

Usage examples:
    lintdiff before.json after.json
    lintdiff --format md before.json after.json
    ruff check . --output-format json > before.json
    ruff check . --output-format json > after.json
    lintdiff before.json after.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class Issue:
    path: str
    lineno: int
    code: str
    message: str


def _load(path: str) -> List[Issue]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        # ruff wrapped result
        data = data.get("files", data.get("results", [data]))
    if not isinstance(data, list):
        data = [data]
    issues: List[Issue] = []
    for entry in data:
        path = entry.get("path", "")
        for row in entry.get("issues", entry.get("rows", entry.get("results", []))):
            issues.append(
                Issue(
                    path=str(row.get("path", path)),
                    lineno=int(row.get("line", row.get("lineno", 0)) or 0),
                    code=str(row.get("code", row.get("rule_id", ""))),
                    message=str(row.get("message", row.get("description", ""))),
                )
            )
    return issues


def _index(issues: Sequence[Issue]) -> dict[tuple[str, int, str], Issue]:
    out: dict[tuple[str, int, str], Issue] = {}
    for issue in issues:
        out[(issue.path, issue.lineno, issue.code)] = issue
    return out


def diff(before: List[Issue], after: List[Issue]) -> Tuple[List[Issue], List[Issue], List[Issue]]:
    before_index = _index(before)
    after_index = _index(after)
    added = [issue for key, issue in after_index.items() if key not in before_index]
    removed = [issue for key, issue in before_index.items() if key not in after_index]
    common_keys = before_index.keys() & after_index.keys()
    unchanged = [after_index[key] for key in sorted(common_keys)]
    return added, removed, unchanged


def render_plain(added: List[Issue], removed: List[Issue], unchanged: List[Issue]) -> str:
    parts: List[str] = []
    if added:
        parts.append("added:")
        for issue in added:
            parts.append(f"+ {issue.code} {issue.path}:{issue.lineno}: {issue.message}")
    if removed:
        parts.append("removed:")
        for issue in removed:
            parts.append(f"- {issue.code} {issue.path}:{issue.lineno}: {issue.message}")
    if not parts:
        return "No lint rule changes detected."
    return "\n".join(parts)


def render_markdown(added: List[Issue], removed: List[Issue], unchanged: List[Issue]) -> str:
    lines = ["# lintdiff", ""]
    lines.append(f"- added: {len(added)}")
    lines.append(f"- removed: {len(removed)}")
    lines.append(f"- unchanged: {len(unchanged)}")
    lines.append("")
    if added:
        lines.append("## added")
        lines.append("")
        for issue in added:
            lines.append(f"- `{issue.code}` `{issue.path}:{issue.lineno}` — {issue.message}")
        lines.append("")
    if removed:
        lines.append("## removed")
        lines.append("")
        for issue in removed:
            lines.append(f"- `{issue.code}` `{issue.path}:{issue.lineno}` — {issue.message}")
        lines.append("")
    if not added and not removed:
        lines.append("No lint rule changes detected.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lintdiff",
        description="Show changed lint rules between two lint reports.",
    )
    parser.add_argument("before", help="Path to previous lint report")
    parser.add_argument("after", help="Path to current lint report")
    parser.add_argument(
        "--format",
        choices=("plain", "markdown"),
        default="plain",
        help="Output format (default: plain)",
    )
    parser.add_argument(
        "--only",
        choices=("added", "removed"),
        default=None,
        help="Show only added or removed rules",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        before = _load(args.before)
        after = _load(args.after)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"lintdiff: {exc}", file=sys.stderr)
        return 1
    added, removed, unchanged = diff(before, after)
    if args.only == "added":
        payload = render_plain(added, [], unchanged)
    elif args.only == "removed":
        payload = render_plain([], removed, unchanged)
    else:
        payload = render_markdown(added, removed, unchanged) if args.format == "markdown" else render_plain(added, removed, unchanged)
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "Issue",
    "diff",
    "main",
    "render_markdown",
    "render_plain",
]
