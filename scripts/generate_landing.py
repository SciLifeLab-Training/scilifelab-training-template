#!/usr/bin/env python3
"""
Validate the landing page data and generate the landing page.

Runs as the Quarto pre-render step on the main branch. It reads the
data files in data/, checks them, and writes:

- the landing page sections to _generated/ (included by _sections/);
- the Bioschemas markup of the training to _generated/bioschemas.html;
- CITATION.cff, .zenodo.json and the generated blocks of README.md.

In template mode (website.template: true), the citation files and
README describe the template itself, from the files in _template/.
"""

from __future__ import annotations

import html
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


SCRIPTS_DIR = Path(__file__).resolve().parent

# Make scripts/renderers importable, also when this module is imported
# by the tests as scripts.generate_landing.
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from renderers.fair import (  # noqa: E402
    licence_id,
    render_bioschemas,
    write_fair_files,
)
from renderers.footer import render_footer  # noqa: E402
from renderers.landing import (  # noqa: E402
    render_bottom_cards,
    render_hero_brand,
    render_hero_copy,
    render_instances_band_media,
    render_template_banner,
    render_top_cards,
)


ROOT = SCRIPTS_DIR.parent
DATA_DIR = ROOT / "data"
INSTANCES_FILE = DATA_DIR / "instances.yml"
COURSE_FILE = DATA_DIR / "course.yml"
TEAM_FILE = DATA_DIR / "team.yml"
WEBSITE_FILE = DATA_DIR / "website.yml"
TEMPLATE_DIR = ROOT / "_template"
GENERATED_DIR = ROOT / "_generated"
HERO_ACTIONS_FILE = GENERATED_DIR / "hero-actions.qmd"
INSTANCES_BAND_FILE = GENERATED_DIR / "instances-band.qmd"

DOI_PATTERN = r"^(https?://(dx\.)?doi\.org/|doi:)?10\.\d{4,9}/\S+$"
ORCID_PATTERN = r"^(https://orcid\.org/)?\d{4}-\d{4}-\d{4}-\d{3}[\dX]$"
GITHUB_REPOSITORY_PATTERN = r"^https://github\.com/[^/\s]+/[^/\s]+?/?$"
ALLOWED_ROLES = ("Founder", "Contributor")

class ValidationError(ValueError):
    """Raised when YAML data fails validation."""


UI_DEFAULTS = {
    "hero_view_current_label": "View current instance",
    "hero_registration_open_label": "Registration open!",
    "instances_band_title": "All course instances",
}


def esc_text(value: Any) -> str:
    text = str(value).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
    return html.escape(text, quote=False)


def esc_url(value: str) -> str:
    return value.replace("<", "%3C").replace(">", "%3E")


def format_link(label: str, href: str, classes: list[str]) -> str:
    class_attrs = " ".join(f".{css_class}" for css_class in classes)
    return f"[{esc_text(label)}](<{esc_url(href)}>){{{class_attrs}}}"


def load_yaml_dict(path: Path) -> dict[str, Any]:
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict):
        path_label = str(path)
        try:
            path_label = str(path.relative_to(ROOT))
        except ValueError:
            pass
        raise ValidationError(
            f"{path_label} must contain a top-level mapping/object."
        )
    return content


def validate_labels(content: Any) -> dict[str, str]:
    """Check website.labels and fill in the default for a missing label."""

    if content is None:
        return UI_DEFAULTS.copy()

    if not isinstance(content, dict):
        raise ValidationError("website.labels must be a mapping.")

    unknown_keys = sorted(set(content.keys()) - set(UI_DEFAULTS.keys()))
    if unknown_keys:
        unknown_fmt = ", ".join(repr(key) for key in unknown_keys)
        raise ValidationError(
            "website.labels contains unknown key(s): "
            f"{unknown_fmt}. Allowed keys: {', '.join(UI_DEFAULTS.keys())}."
        )

    labels = UI_DEFAULTS.copy()
    for key, default in UI_DEFAULTS.items():
        value = content.get(key, default)
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(
                f"website.labels.{key} must be a non-empty string when provided."
            )
        labels[key] = value

    return labels


def _require_string(data: dict[str, Any], key: str, context: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{context}.{key} must be a non-empty string.")
    return value


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_relative_url(value: str) -> bool:
    return value.startswith("./") or (
        value.startswith("/") and not value.startswith("//")
    )


def _validate_slug(slug: str, context: str) -> None:
    if not re.fullmatch(r"\d{4}", slug):
        raise ValidationError(f"{context}.slug must be exactly 4 digits (got {slug!r}).")
    if slug == "0000":
        return

    month = int(slug[2:])
    if month < 1 or month > 12:
        raise ValidationError(
            f"{context}.slug month must be between 01 and 12 (got {slug!r})."
        )


def _validate_instance_url(url: str, context: str) -> None:
    if re.fullmatch(r"\./\d{4}/", url):
        return
    if _is_http_url(url):
        return
    raise ValidationError(
        f"{context}.instance_url must be './NNNN/' or an absolute http(s) URL."
    )


def _validate_registration_url(url: str, context: str) -> None:
    if not url:
        return
    if url.startswith("//"):
        raise ValidationError(
            f"{context}.registration_url must not be protocol-relative (//...)."
        )
    if _is_http_url(url) or _is_relative_url(url):
        return
    raise ValidationError(
        f"{context}.registration_url must be empty, relative, or absolute http(s)."
    )


def validate_instances_data(data: dict[str, Any]) -> list[dict[str, Any]]:
    instances = data.get("instances")
    if not isinstance(instances, list) or not instances:
        raise ValidationError("instances.yml must define a non-empty 'instances' list.")

    normalized: list[dict[str, Any]] = []
    seen_slugs: set[str] = set()

    for index, raw in enumerate(instances):
        context = f"instances[{index}]"
        if not isinstance(raw, dict):
            raise ValidationError(f"{context} must be an object/mapping.")

        slug = _require_string(raw, "slug", context)
        _validate_slug(slug, context)
        if slug in seen_slugs:
            raise ValidationError(f"{context}.slug {slug!r} is duplicated.")
        seen_slugs.add(slug)

        label = _require_string(raw, "label", context)
        status = _require_string(raw, "status", context)
        if status not in {"current", "previous"}:
            raise ValidationError(f"{context}.status must be 'current' or 'previous'.")

        visible = raw.get("visible")
        if not isinstance(visible, bool):
            raise ValidationError(f"{context}.visible must be a boolean.")
        
        show_in_hero = raw.get("show_in_hero", True)
        if not isinstance(show_in_hero, bool):
            raise ValidationError(f"{context}.show_in_hero must be a boolean.")

        instance_url = _require_string(raw, "instance_url", context)
        _validate_instance_url(instance_url, context)
        if (
            re.fullmatch(r"\./\d{4}/", instance_url)
            and instance_url != f"./{slug}/"
        ):
            raise ValidationError(
                f"{context}.instance_url must match slug for relative links "
                f"(expected './{slug}/', got {instance_url!r})."
            )

        registration_url = raw.get("registration_url", "")
        if registration_url is None:
            registration_url = ""
        if not isinstance(registration_url, str):
            raise ValidationError(f"{context}.registration_url must be a string.")
        _validate_registration_url(registration_url, context)

        sort_key = raw.get("sort_key")
        if isinstance(sort_key, bool) or not isinstance(sort_key, int):
            raise ValidationError(f"{context}.sort_key must be an integer.")

        normalized.append(
            {
                "slug": slug,
                "label": label,
                "status": status,
                "visible": visible,
                "show_in_hero": show_in_hero,
                "instance_url": instance_url,
                "registration_url": registration_url,
                "sort_key": sort_key,
            }
        )

    current_instances = [item for item in normalized if item["status"] == "current"]
    if len(current_instances) != 1:
        raise ValidationError("instances.yml must contain exactly one status='current' entry.")
    if not current_instances[0]["visible"]:
        raise ValidationError("The current instance must be visible: true.")

    return normalized


def _render_hero_actions(current: dict[str, Any], ui_labels: dict[str, str]) -> str:
    actions = []

    if current["show_in_hero"]:
        actions.append(
            "- "
            + format_link(
                ui_labels["hero_view_current_label"],
                current["instance_url"],
                ["hero-cta", "hero-cta--primary"],
            )
        )

    if current["registration_url"]:
        actions.append(
            "- "
            + format_link(
                ui_labels["hero_registration_open_label"],
                current["registration_url"],
                ["hero-cta", "hero-cta--secondary"],
            )
        )

    return "\n".join(actions) + "\n"


def _render_instance_pills(visible_instances: list[dict[str, Any]]) -> str:
    buttons = []
    for item in visible_instances:
        classes = ["instance-pill"]
        if item["status"] == "current":
            classes.append("instance-pill--current")
        buttons.append(
            "- "
            + format_link(
                item["label"],
                item["instance_url"],
                classes,
            )
        )
    return "\n".join(buttons)


def _render_instances_band(instances: list[dict[str, Any]], ui_labels: dict[str, str]) -> str:
    current = next(item for item in instances if item["status"] == "current")
    visible_instances = [item for item in instances if item["visible"]]
    previous = sorted(
        [item for item in visible_instances if item["slug"] != current["slug"]],
        key=lambda item: item["sort_key"],
        reverse=True,
    )
    ordered_instances = [current, *previous]
    instance_pills = _render_instance_pills(ordered_instances)

    return f"""
::: {{.section-title .instances-band__title}}
{esc_text(ui_labels["instances_band_title"])}
:::

::: {{.instance-grid .instance-grid--band}}
{instance_pills}
:::
""".strip() + "\n"


def build_dynamic_partials(
    instances: list[dict[str, Any]], ui_labels: dict[str, str]
) -> tuple[str, str, str]:
    current = next(item for item in instances if item["status"] == "current")
    return (
        _render_hero_actions(current, ui_labels),
        _render_instances_band(instances, ui_labels),
    )


def write_generated_partials(
    instances: list[dict[str, Any]], ui_labels: dict[str, str]
) -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    hero_actions, instances_band = build_dynamic_partials(
        instances, ui_labels
    )
    HERO_ACTIONS_FILE.write_text(hero_actions, encoding="utf-8")
    INSTANCES_BAND_FILE.write_text(instances_band, encoding="utf-8")

# ---------------------------------------------------------
# Course, team and website data
# ---------------------------------------------------------

def _load_section(path: Path, key: str) -> dict[str, Any]:
    """Load the mapping under a top-level key, e.g. 'course'."""

    content = load_yaml_dict(path)
    section = content.get(key)

    if not isinstance(section, dict):
        raise ValidationError(
            f"{path.name} must contain a '{key}' mapping."
        )

    return section


def _check_list(value: Any, field: str, required: bool = False) -> None:
    if value in (None, "") and not required:
        return
    if not isinstance(value, list):
        raise ValidationError(f"{field} must be a list.")
    if required and not [item for item in value if str(item or "").strip()]:
        raise ValidationError(f"{field} must contain at least one item.")


def validate_course(course: dict[str, Any]) -> dict[str, Any]:
    """Check data/course.yml (the training as a whole)."""

    for field in ("title", "description"):
        if not str(course.get(field) or "").strip():
            raise ValidationError(f"course.{field} is required.")

    _check_list(course.get("learning_outcomes"), "course.learning_outcomes", True)
    _check_list(course.get("keywords"), "course.keywords", True)
    _check_list(course.get("topics"), "course.topics")
    _check_list(course.get("organizers"), "course.organizers")
    _check_list(course.get("funding"), "course.funding")

    reuse = course.get("reuse") or {}
    if not isinstance(reuse, dict):
        raise ValidationError("course.reuse must be a mapping.")

    # A licence is needed for the citation, Zenodo and Bioschemas, and must
    # be one fair.py recognises, or be given as an SPDX code in licence_id.
    if not str(reuse.get("licence") or reuse.get("licence_id") or "").strip():
        raise ValidationError(
            'course.reuse.licence is required, for example "CC BY 4.0".'
        )

    if not licence_id(course):
        raise ValidationError(
            f"course.reuse.licence {reuse.get('licence')!r} is not recognised. "
            "Add its short code from https://spdx.org/licenses/ to "
            "course.reuse.licence_id."
        )
    
    for field in ("doi", "version_doi"):
        value = str(reuse.get(field) or "").strip()
        if value and not re.match(DOI_PATTERN, value, re.IGNORECASE):
            raise ValidationError(
                f"course.reuse.{field} is not a valid DOI: {value!r}. "
                'Write it like "10.5281/zenodo.1234567".'
            )

    release_date = str(reuse.get("release_date") or "").strip()
    if release_date:
        try:
            date.fromisoformat(release_date)
        except ValueError:
            raise ValidationError(
                f"course.reuse.release_date is not a valid date: "
                f"{release_date!r}. Write it as YYYY-MM-DD."
            ) from None

    return course


def complete_names(team: dict[str, Any]) -> dict[str, Any]:
    """Build each member's display name from given_names and family_names."""

    for member in team.get("members") or []:
        if not isinstance(member, dict) or str(member.get("name") or "").strip():
            continue
        parts = [
            str(member.get("given_names") or "").strip(),
            str(member.get("family_names") or "").strip(),
        ]
        member["name"] = " ".join(part for part in parts if part)

    return team


def validate_team(team: dict[str, Any]) -> dict[str, Any]:
    """Check data/team.yml (Founders and Contributors)."""

    members = team.get("members")

    if not isinstance(members, list) or not members:
        raise ValidationError("team.members must contain at least one member.")

    for index, member in enumerate(members):
        if not isinstance(member, dict):
            raise ValidationError(f"team.members[{index}] must be a mapping.")

        name = str(member.get("name") or "").strip()
        if not name:
            raise ValidationError(
                "A team member is missing a name: fill in "
                "'given_names' and 'family_names'."
            )

        roles = member.get("roles")
        if not isinstance(roles, list) or not roles:
            raise ValidationError(
                f"Team member '{name}' must have a list of roles."
            )

        invalid = sorted(set(roles) - set(ALLOWED_ROLES))
        if invalid:
            raise ValidationError(
                f"Team member '{name}' has invalid role(s): "
                f"{', '.join(map(str, invalid))}. "
                f"Allowed roles are: {', '.join(ALLOWED_ROLES)}."
            )

        if not str(member.get("affiliation") or "").strip():
            raise ValidationError(f"Team member '{name}' is missing 'affiliation'.")

        orcid = str(member.get("orcid") or "").strip()
        if orcid and not re.match(ORCID_PATTERN, orcid):
            raise ValidationError(
                f"Team member '{name}' has an invalid ORCID: {orcid!r}. "
                'Write it like "https://orcid.org/0000-0002-1825-0097".'
            )

        if member.get("course_contact") is True and not member.get("email"):
            raise ValidationError(
                f"Team member '{name}' is marked as course_contact "
                "but has no email address."
            )

    # CITATION.cff and Zenodo need at least one author.
    if all(member.get("citation_author") is False for member in members):
        raise ValidationError(
            "At least one team member must be a citation author: remove "
            "'citation_author: false' from at least one member."
        )
    
    return team


def validate_website(website: dict[str, Any]) -> dict[str, Any]:
    """Check data/website.yml."""

    if not isinstance(website.get("template", False), bool):
        raise ValidationError("website.template must be true or false.")

    logos = (website.get("hero") or {}).get("logos") or []
    _check_list(logos, "website.hero.logos")
    for index, logo in enumerate(logos):
        if not isinstance(logo, dict) or not str(logo.get("src") or "").strip():
            raise ValidationError(f"website.hero.logos[{index}] needs a 'src'.")
        if not isinstance(logo.get("primary", False), bool):
            raise ValidationError(
                f"website.hero.logos[{index}].primary must be true or false."
            )
        height = logo.get("height")
        if height not in (None, "") and (
            isinstance(height, bool)
            or not isinstance(height, (int, float))
            or height <= 0
        ):
            raise ValidationError(
                f"website.hero.logos[{index}].height must be a positive "
                f"number of pixels, for example 56. Got: {height!r}"
            )

    if sum(1 for logo in logos if logo.get("primary") is True) > 1:
        raise ValidationError(
            "Only one logo in website.hero.logos can have 'primary: true'."
        )

    footer = website.get("footer") or {}
    repository = str((footer.get("repository") or {}).get("url") or "").strip()

    if not re.match(GITHUB_REPOSITORY_PATTERN, repository):
        raise ValidationError(
            "website.footer.repository.url must be the GitHub address of "
            "this repository, for example "
            '"https://github.com/organisation/repository"'
        )

    website["labels"] = validate_labels(website.get("labels"))

    return website


def load_landing_data() -> tuple[dict, dict, dict]:
    """Load and check course.yml, team.yml and website.yml."""

    course = validate_course(_load_section(COURSE_FILE, "course"))
    team = validate_team(complete_names(_load_section(TEAM_FILE, "team")))
    website = validate_website(_load_section(WEBSITE_FILE, "website"))

    return course, team, website


def load_citation_data(
    course: dict[str, Any], team: dict[str, Any], website: dict[str, Any]
) -> tuple[dict, dict]:
    """
    Return the course and team to describe in the citation files.

    In template mode these are the template's own metadata in
    _template/, otherwise the training's data files.
    """

    if website.get("template") is not True:
        return course, team

    template_course = validate_course_metadata(
        _load_section(TEMPLATE_DIR / "course.yml", "course")
    )
    template_team = validate_team(
        complete_names(_load_section(TEMPLATE_DIR / "team.yml", "team"))
    )

    return template_course, template_team


def validate_course_metadata(course: dict[str, Any]) -> dict[str, Any]:
    """Check _template/course.yml: a title and description are enough."""

    for field in ("title", "description"):
        if not str(course.get(field) or "").strip():
            raise ValidationError(f"_template/course.yml: course.{field} is required.")

    return course


# ---------------------------------------------------------
# Writing the landing page
# ---------------------------------------------------------

def write_landing_sections(
    course: dict[str, Any], team: dict[str, Any], website: dict[str, Any]
) -> None:
    """Write the data-driven landing page sections to _generated/."""

    sections = {
        "template-banner.qmd": render_template_banner(website),
        "hero-brand.qmd": render_hero_brand(website),
        "hero-copy.qmd": render_hero_copy(course),
        "top-cards.qmd": render_top_cards(course),
        "instances-band-media.qmd": render_instances_band_media(website),
        "bottom-cards.qmd": render_bottom_cards(team),
        "footer.qmd": render_footer(website),
        # Page metadata for index.qmd: the browser tab title and the
        # description used by search engines and link previews.
        "page-metadata.yml": yaml.safe_dump(
            {
                "pagetitle": " ".join(str(course.get("title")).split()),
                "description-meta": " ".join(
                    str(course.get("subtitle") or course.get("description")).split()
                ),
            },
            allow_unicode=True,
            sort_keys=False,
            width=1000,
        ),
        
        # No Bioschemas in template mode: the page then shows an
        # example training, which should not be listed as a real course.
        "bioschemas.html": (
            ""
            if website.get("template") is True
            else render_bioschemas(course, team, website, scope="course") + "\n"
        ),
    }

    for name, content in sections.items():
        (GENERATED_DIR / name).write_text(content, encoding="utf-8")


def main() -> None:
    instances_data = load_yaml_dict(INSTANCES_FILE)
    instances = validate_instances_data(instances_data)
    course, team, website = load_landing_data()

    # Start every render with a clean generated directory.
    if GENERATED_DIR.exists():
        shutil.rmtree(GENERATED_DIR)

    write_generated_partials(instances, website["labels"])
    write_landing_sections(course, team, website)

    citation_course, citation_team = load_citation_data(course, team, website)
    write_fair_files(
        ROOT,
        citation_course,
        citation_team,
        website,
        source="_template/" if website.get("template") is True else "data/",
        scope="course",
    )

    print("Generated the landing page sections in", GENERATED_DIR.relative_to(ROOT))


if __name__ == "__main__":
    try:
        main()
    except ValidationError as exc:
        print(f"ValidationError: {exc}")
        raise SystemExit(1) from exc
