"""Preview the training instance website, and update it when a data file changes.

Run this instead of `quarto preview`:

    python scripts/preview.py

Quarto's own preview only updates when a page file (.qmd) changes. The
website is built from the files in data/, so this script starts the
normal preview and also watches data/. When you save a data file, it
rebuilds the generated parts of the website and tells the preview to
refresh the page you are looking at. Other pages are refreshed when you
open them.

Stop it with Ctrl+C, as with `quarto preview`.
"""

from __future__ import annotations

import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCHED = [ROOT / "data"]
GENERATOR = ROOT / "scripts" / "render_course.py"
CHECK_EVERY = 0.5  # seconds
MARKER = b"\n<!-- preview refresh -->\n"
COLOURS = re.compile(r"\x1b\[[0-9;]*m")
REQUEST = re.compile(r"GET: (/\S*)")


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


def generate() -> bool:
    """Rebuild the generated parts. Return False when a data file has a
    problem."""
    result = subprocess.run(
        [sys.executable, str(GENERATOR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("\nThe website could not be updated:", flush=True)
        print((result.stderr or result.stdout).strip(), flush=True)
        print("Fix the data file and save it again.\n", flush=True)
        return False
    return True


def page_for(url: str) -> Path | None:
    """Return the page file (.qmd) for an address the browser opened."""
    url = url.split("?")[0].split("#")[0]
    if url.endswith("/"):
        url += "index.html"
    if not url.endswith(".html"):
        return None
    page = ROOT / (url.lstrip("/")[: -len(".html")] + ".qmd")
    return page if page.is_file() else None


def refresh(page: Path) -> None:
    """Make the preview re-render one page.

    Quarto only re-renders a page when the content of its file changes,
    so briefly add an invisible comment to the file and then remove it
    again. The file ends up exactly as it was. If you save the file
    yourself in the meantime, your version is kept.
    """
    try:
        original = page.read_bytes()
        page.write_bytes(original + MARKER)
        time.sleep(1.5)
        if page.read_bytes() == original + MARKER:
            page.write_bytes(original)
    except OSError:
        pass


def follow(stream, opened: "queue.Queue[Path]") -> None:
    """Pass on Quarto's messages, and note which pages the browser opens."""
    for line in stream:
        sys.stdout.write(line)
        sys.stdout.flush()
        match = REQUEST.search(COLOURS.sub("", line))
        if match:
            page = page_for(match.group(1))
            if page is not None:
                opened.put(page)


def main() -> int:
    quarto = shutil.which("quarto")
    if quarto is None:
        print("Quarto was not found. Is it installed?", file=sys.stderr)
        return 1

    # Build the generated parts first. Newer versions of Quarto stop
    # with "Include directive failed" when they are missing.
    result = subprocess.run([sys.executable, str(GENERATOR)], cwd=ROOT)
    if result.returncode != 0:
        print("\nFix the data file above, then start the preview again.",
              file=sys.stderr)
        return 1

    preview = subprocess.Popen(
        [quarto, "preview", *sys.argv[1:]],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    opened: "queue.Queue[Path]" = queue.Queue()
    threading.Thread(
        target=follow, args=(preview.stdout, opened), daemon=True
    ).start()

    current: Path | None = None
    outdated: set[Path] = set()
    last = snapshot()
    try:
        while preview.poll() is None:
            time.sleep(CHECK_EVERY)

            # Pages the browser opened since the last check.
            while not opened.empty():
                page = opened.get()
                current = page
                if page in outdated:
                    outdated.discard(page)
                    refresh(page)

            # Data files that changed since the last check.
            now = snapshot()
            if now != last:
                last = now
                if generate():
                    outdated = {
                        page
                        for page in ROOT.rglob("*.qmd")
                        if not page.name.startswith("_")
                        and "_site" not in page.parts
                    }
                    print("Data changed: updating the preview.", flush=True)
                    if current is not None:
                        outdated.discard(current)
                        refresh(current)
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