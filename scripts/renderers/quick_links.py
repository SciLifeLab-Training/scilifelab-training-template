"""
The quick links on the overview page: up to four cards that lead to
the most important pages.

Content and Syllabus are always shown. The other pages are shown only
when they also appear in the navigation bar, that is, when their data
file contains information, and only while there is room.

The title, description and icon of each card come from "pages" in
data/website.yml. An entry that is missing there:

- for Content and Syllabus: uses the standard texts below;
- for the other pages: means the page gets no quick link. It stays in
  the navigation bar.
"""

from html import escape

# The order in which pages are considered, and the standard texts for
# Content and Syllabus.
PRIORITY = [
    "content",
    "syllabus",
    "schedule",
    "practicalities",
    "preparation",
    "resources",
    "faq",
]

ALWAYS_SHOWN = {
    "content": {
        "title": "Content",
        "description": "Modules, slides and exercises",
        "icon": "folder",
        "href": "content/index.qmd",
    },
    "syllabus": {
        "title": "Syllabus",
        "description": "Description, learning outcomes and prerequisites",
        "icon": "journal-text",
        "href": "syllabus.qmd",
    },
}

# The page each quick link leads to, when the entry doesn't say.
DEFAULT_HREFS = {key: f"{key}.qmd" for key in PRIORITY}
DEFAULT_HREFS["content"] = "content/index.qmd"

MAXIMUM = 4


def _card(key, entry):
    """One quick link card. Missing fields fall back to sensible texts."""

    standard = ALWAYS_SHOWN.get(key, {})

    title = str(entry.get("title") or standard.get("title") or key.capitalize())
    description = str(entry.get("description") or standard.get("description") or "")
    icon = str(entry.get("icon") or standard.get("icon") or "link-45deg")
    href = str(entry.get("href") or DEFAULT_HREFS[key])

    return f"""
<div class="course-link-card">

<i class="bi bi-{escape(icon, quote=True)} course-link-icon"></i>

<div class="course-link-content">

<h3>{escape(title)}</h3>

<p>{escape(description)}</p>

<a class="course-text-link" href="{escape(href, quote=True)}">
View {escape(title.lower())} →
</a>

</div>

</div>
""".strip()


def render_quick_links(website, available_pages):
    """Render up to four homepage quick links."""

    pages = website.get("pages") or {}

    cards = []

    for key in PRIORITY:

        if len(cards) >= MAXIMUM:
            break

        entry = pages.get(key)

        if key in ALWAYS_SHOWN:
            cards.append(_card(key, entry or {}))
            continue

        # The other pages: only when they are in the navigation bar,
        # and only when they have an entry in website.yml.
        if key not in available_pages or not isinstance(entry, dict):
            continue

        cards.append(_card(key, entry))

    if not cards:
        return ""

    return (
        '<div class="course-links">\n'
        '\n'
        '<div class="course-section-label">\n'
        '\n'
        'QUICK LINKS\n'
        '\n'
        '</div>\n'
        '\n'
        '<div class="course-links-grid">\n'
        + "\n".join(cards)
        + "\n</div>\n"
        '\n'
        '</div>'
    ).strip()
