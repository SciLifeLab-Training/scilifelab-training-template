#!/usr/bin/env python3
"""
Compare two template versions, for the weekly update check.

Used by .github/workflows/check-template-update.yml:

    python scripts/check_template_version.py CURRENT LATEST

prints "update" when LATEST is newer than CURRENT, and "current"
otherwise. Versions look like "1.2.0", "v1.2.0" or "1.0.0-alpha".
A final version is newer than a pre-release of the same number:
1.0.0 is newer than 1.0.0-alpha.
"""

from __future__ import annotations

import re
import sys


def parse(version: str) -> tuple:
    """Turn "v1.2.0-alpha" into ((1, 2, 0), "alpha") for comparing."""

    text = version.strip().lstrip("vV")
    number, _, pre = text.partition("-")
    parts = []

    for piece in number.split("."):
        digits = re.match(r"\d+", piece)
        parts.append(int(digits.group()) if digits else 0)

    # Pad, so 1.2 and 1.2.0 are equal.
    while len(parts) < 3:
        parts.append(0)

    # No pre-release sorts after any pre-release: (1, "") > (0, "alpha").
    return tuple(parts), (1, "") if not pre else (0, pre)


def is_newer(latest: str, current: str) -> bool:
    return parse(latest) > parse(current)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: check_template_version.py CURRENT LATEST", file=sys.stderr)
        return 2

    current, latest = argv[1], argv[2]
    print("update" if is_newer(latest, current) else "current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
