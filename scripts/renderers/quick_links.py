def render_quick_links(website, available_pages):

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

        # Content and Syllabus are always shown. The other pages are
        # shown only when they are also in the navbar.
        if key not in ("content", "syllabus") and key not in available_pages:
            continue

        cards.append(
            f"""
<div class="course-link-card">

<i class="bi bi-{page["icon"]} course-link-icon"></i>

<div class="course-link-content">

<h3>{page["title"]}</h3>

<p>{page["description"]}</p>

<a class="course-text-link" href="{page["href"]}">
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