#!/usr/bin/env python3
"""
Guard against real, sensitive identifiers leaking into the book's content.

This project is built from a real production observability implementation,
but every name, domain, account ID, and other identifying detail must be
scrubbed before it reaches docs/. This script re-checks that discipline on
every PR so a future edit (by a person or by an AI session with no memory
of the earlier scrubbing work) can't accidentally reintroduce something
sensitive.

Exit code is non-zero if anything is found — CI fails the PR.
"""

import re
import sys
import unicodedata
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

# Known real identifiers that must never appear in the book, established
# while writing it from the source infrastructure repo. Extend this list
# whenever a new real identifier is discovered during content review —
# treat it as a living list, not a one-time snapshot.
FORBIDDEN_LITERALS = [
    "sunairio",
    "sunairio-ui",
    "sunairio-models",
    "sunairio.internal",
    "sunairio.grafana.net",
    "039365534375",  # real AWS account ID
    "i-0284ad2a4f33a8341",  # real EC2 instance ID
    "xgZvi7vopS",  # real session ID used once as an "illustrative" example
    "cacher_step_duration_seconds_count",  # real custom metric name
    "robbygrathwohl",  # real developer username seen in CloudTrail records
    "Ørsted",
    "Danske Commodities",
    "Constellation Energy",
    "Duke Energy",
]

# Structural patterns for identifier *shapes* rather than specific known
# values — catches a new leak even if it isn't on the literal list above.
FORBIDDEN_PATTERNS = [
    (r"\bi-[0-9a-f]{8,17}\b", "AWS instance ID"),
    (r"\bsg-[0-9a-f]{8,17}\b", "AWS security group ID"),
    (r"\b\d{12}\b", "12-digit number (possible AWS account ID)"),
    (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "IPv4 address"),
    (r"[\w.+-]+@[\w-]+\.[\w.-]+", "email address"),
]


def scan_file(path: Path):
    findings = []
    text = path.read_text(encoding="utf-8")

    for lineno, line in enumerate(text.splitlines(), start=1):
        for literal in FORBIDDEN_LITERALS:
            if literal.lower() in line.lower():
                findings.append((lineno, "forbidden-literal", literal, line.strip()))
        for pattern, label in FORBIDDEN_PATTERNS:
            for m in re.finditer(pattern, line):
                findings.append((lineno, label, m.group(0), line.strip()))

    cyrillic = [c for c in text if "CYRILLIC" in unicodedata.name(c, "")]
    if cyrillic:
        findings.append((None, "cyrillic-homoglyph", "".join(sorted(set(cyrillic))), ""))

    return findings


def main():
    if not DOCS_DIR.is_dir():
        print(f"docs/ directory not found at {DOCS_DIR}", file=sys.stderr)
        return 1

    any_findings = False
    for path in sorted(DOCS_DIR.glob("*.md")):
        findings = scan_file(path)
        for lineno, kind, match, context in findings:
            any_findings = True
            loc = f"{path.relative_to(DOCS_DIR.parent)}:{lineno}" if lineno else str(
                path.relative_to(DOCS_DIR.parent)
            )
            print(f"::error file={path}::{loc} [{kind}] {match!r}  |  {context}")

    if any_findings:
        print(
            "\nAnonymization check FAILED — a real/sensitive identifier or "
            "stray Cyrillic character was found above. If this is a false "
            "positive (e.g. a generic 12-digit number that isn't an AWS "
            "account ID), narrow the pattern in scripts/check_anonymization.py "
            "rather than deleting the check.",
            file=sys.stderr,
        )
        return 1

    print(f"Anonymization check passed — {len(list(DOCS_DIR.glob('*.md')))} files clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
