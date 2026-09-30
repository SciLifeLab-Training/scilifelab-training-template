from pathlib import Path


def render_quick_links(website, schedule_events):

    """Render up to four homepage quick links."""

    pages = website["pages"]

    priority = [
        "content",
        "syllabus",
        "schedule",
        "practicalities",
        "preparation",
        "resources",
        "faq",
    ]

    cards = []

    for key in priority:

        if len(cards) >= 4:
            break

        page = pages[key]

        # Schedule is available only when events exist.
        if key == "schedule":

            if not schedule_events:
                continue

        # Course Content and Course Syllabus are always available.
        elif key in ["content", "syllabus"]:

            pass

        # All other pages are available only when
        # their QMD file contains meaningful body content.
        else:

            path = Path(page["href"])

            if not path.exists():
                continue

            content = path.read_text(encoding="utf-8")

            # Remove YAML front matter.
            if content.startswith("---"):

                parts = content.split("---", 2)

                if len(parts) == 3:
                    content = parts[2]

            # Ignore whitespace-only pages.
            if not content.strip():
                continue

        cards.append(
            f"""
<div class="course-link-card">

<i class="bi bi-{page["icon"]} course-link-icon"></i>

<div class="course-link-content">

<h3>{page["title"]}</h3>

<p>{page["description"]}</p>

<a href="{page["href"]}">
View {page["title"].lower()} →
</a>

</div>

</div>
""".strip()
        )

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