from pathlib import Path
import re
import yaml

from loaders import yaml_error_message


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"


def load_content_sections(content):
    sections = content.get("sections", [])

    result = []

    for section in sections:

        section_id = section["id"]
        section_dir = CONTENT_DIR / section_id

        if not section_dir.exists():
            raise ValueError(
                f"Content section '{section_id}' does not exist: "
                f"{section_dir}"
            )

        pages = []

        for path in section_dir.glob("*.qmd"):

            text = path.read_text(encoding="utf-8")

            label = path.relative_to(ROOT).as_posix()
            title = extract_front_matter_value(text, "title", label)
            order = extract_front_matter_value(text, "order", label)

            if not title:
                raise ValueError(
                    f"Content page '{path}' is missing a title"
                )

            pages.append({
                "title": title,
                "path": path,
                "order": int(order) if order else None,
            })

        has_order = any(page["order"] is not None for page in pages)

        if has_order and any(page["order"] is None for page in pages):
            raise ValueError(
                f"Section '{section_id}' mixes pages with and without order"
            )

        if has_order:
            pages.sort(key=lambda page: page["order"])
        else:
            pages.sort(key=lambda page: page["path"].name.lower())

        result.append({
            "id": section_id,
            "label": section["label"],
            "title": section["title"],
            "pages": pages,
        })

    return result


def extract_front_matter_value(text, key, label="this page"):

    if not text.startswith("---"):
        return None

    parts = text.split("---", 2)

    if len(parts) != 3:
        return None

    try:
        front_matter = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as error:
        # parts[1] starts on the first line of the file, so the line
        # numbers in the error match the lines of the page.
        raise ValueError(
            yaml_error_message(f"{label} (the part between the --- lines)", error, text)
        ) from None

    return front_matter.get(key)
