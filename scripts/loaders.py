from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_yaml(filename):
    with open(DATA / filename, encoding="utf-8") as f:
        return yaml.safe_load(f)


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
