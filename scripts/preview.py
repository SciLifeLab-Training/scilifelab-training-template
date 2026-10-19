"""Preview the landing page, and update it when a data file changes.

Run this instead of `quarto preview`:

    python scripts/preview.py

Quarto's own preview only updates when a page file (.qmd) changes. The
landing page is built from the files in data/, so this script starts the
normal preview and also watches data/ (and _template/). When you save a
data file, it rebuilds the landing page sections and tells the preview
to refresh.

Stop it with Ctrl+C, as with `quarto preview`.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCHED = [ROOT / "data", ROOT / "_template"]
GENERATOR = ROOT / "scripts" / "generate_landing.py"
PAGE = ROOT / "index.qmd"
CHECK_EVERY = 1.0  # seconds


def snapshot() -> dict[Path, float]:
    """Return the last-modified time of every file in the watched folders."""
    times: dict[Path, float] = {}
    for folder in WATCHED:
        if not folder.is_dir():
            continue
        for path in folder.rglob("*"):
            if path.is_file() and not path.name.startswith("."):
                try:
                    times[path] = path.stat().st_mtime
                except OSError:
                    pass
    return times


def rebuild() -> None:
    """Rebuild the generated sections, then make the preview refresh."""
    result = subprocess.run(
        [sys.executable, str(GENERATOR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("\nThe landing page could not be updated:", flush=True)
        print((result.stderr or result.stdout).strip(), flush=True)
        print("Fix the data file and save it again.\n", flush=True)
        return
    # Quarto only re-renders when the content of a page file changes, so
    # briefly add an invisible comment to index.qmd and then remove it
    # again. The file ends up exactly as it was.
    original = PAGE.read_bytes()
    try:
        PAGE.write_bytes(original + b"\n<!-- preview refresh -->\n")
        time.sleep(1.5)
    finally:
        PAGE.write_bytes(original)
    print("Data changed: updating the preview.", flush=True)


def main() -> int:
    quarto = shutil.which("quarto")
    if quarto is None:
        print("Quarto was not found. Is it installed?", file=sys.stderr)
        return 1

    preview = subprocess.Popen([quarto, "preview", *sys.argv[1:]], cwd=ROOT)
    last = snapshot()
    try:
        while preview.poll() is None:
            time.sleep(CHECK_EVERY)
            current = snapshot()
            if current != last:
                last = current
                rebuild()
    except KeyboardInterrupt:
        pass
    finally:
        if preview.poll() is None:
            preview.terminate()
            try:
                preview.wait(timeout=10)
            except subprocess.TimeoutExpired:
                preview.kill()
    return 0


if __name__ == "__main__":
    sys.exit(main())
