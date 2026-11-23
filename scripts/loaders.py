from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def yaml_error_message(label, error, text):
    """
    Turn a YAML layout error into a short message for the user.

    Instead of a long Python error, the message names the file and the
    line, shows that line and the one above it (where the mistake often
    is, for example a missing closing quotation mark), and says what to
    check.
    """

    mark = getattr(error, "problem_mark", None) or getattr(error, "context_mark", None)

    # A quotation mark that is never closed is only noticed much further
    # down. The start of the quoted text is where the mistake is.
    if "quoted scalar" in str(getattr(error, "context", "") or ""):
        mark = getattr(error, "context_mark", None) or mark

    if mark is None:
        return f"{label}: the layout of this file is not right ({error})."

    lines = text.splitlines()
    number = mark.line + 1
    shown = []

    for n in (number - 1, number):
        if 1 <= n <= len(lines):
            shown.append(f"    {n:>4} | {lines[n - 1]}")

    return "\n".join([
        f"{label}, line {number}: the layout of the file is not right here,"
        " or on the line just above it.",
        "",
        *shown,
        "",
        "Check that:",
        "- the line starts with the same number of spaces as the lines"
        " that belong with it;",
        "- every quotation mark (\") has a closing quotation mark;",
        "- there are no tabs: use spaces only.",
    ])


def load_yaml(filename):
    text = (DATA / filename).read_text(encoding="utf-8")

    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise ValueError(
            yaml_error_message(f"data/{filename}", error, text)
        ) from None


def load_course():
    return load_yaml("course.yml")["course"]


def load_website():
    return load_yaml("website.yml")["website"]


def load_content():
    return load_yaml("website.yml")["content"]


def load_schedule():
    return load_optional("schedule.yml", "events", [])


def load_team():
    data = load_yaml("team.yml") or {}
    return data.get("team", {})


def load_optional(filename, key, empty):
    """
    Load an optional data file.

    The file may be missing, empty, or contain only comments, or its
    top-level key (for example "faq:") may be empty or left out. In
    all these cases the page simply has no content.
    """

    path = DATA / filename

    if not path.exists():
        return empty

    data = load_yaml(filename) or {}

    if not isinstance(data, dict):
        return empty

    value = data.get(key)

    return value if value else empty


def load_announcements():
    return load_optional("announcements.yml", "announcements", {})


def load_practicalities():
    return load_optional("practicalities.yml", "practicalities", {})


def load_faq():
    return load_optional("faq.yml", "faq", {})


def load_preparation():
    return load_optional("preparation.yml", "preparation", {})


def load_resources():
    return load_optional("resources.yml", "resources", {})
