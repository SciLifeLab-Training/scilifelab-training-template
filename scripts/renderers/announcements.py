from datetime import date


def render_announcements(announcements):

    items = announcements.get("items", [])

    if not items:

        return """
::: {.course-announcements}

<div class="course-announcements-content">

<div class="course-section-label">

ANNOUNCEMENTS

</div>

<div class="course-announcement-empty">

No active announcements.

</div>

</div>

:::
""".strip()

    # Sort newest first.
    items = sorted(
        items,
        key=lambda announcement: announcement["date"],
        reverse=True,
    )

    # Show only the two most recent announcements.
    items = items[:2]

    cards = []

    for announcement in items:

        announcement_date = announcement["date"]

        # Format YYYY-MM-DD as "10 May".
        if isinstance(announcement_date, date):

            formatted_date = announcement_date.strftime("%-d %B")

        else:

            formatted_date = str(announcement_date)

        cards.append(
            f"""
<div class="course-announcement">

<div class="course-announcement-date">{formatted_date}</div>
<h3 class="course-announcement-title">{announcement["title"]}</h3>
<p>{announcement["text"]}</p>
</div>
""".strip()
        )

    return f"""
::: {{.course-announcements}}

<div class="course-announcements-content">

<div class="course-section-label">

ANNOUNCEMENTS

</div>

{"".join(cards)}

<a class="course-announcements-link" href="announcements.qmd">View all announcements →</a>

</div>

:::
""".strip()


def render_announcements_page(announcements):

    items = announcements.get("items", [])
    intro = announcements.get("intro", "")

    if not items:
        return """
<div class="course-announcements-page">

<header class="course-announcements-header">

<div class="course-announcements-label">
Announcements
</div>

<h1>Announcements</h1>

<p class="course-announcements-intro">
There are currently no announcements.
</p>

</header>

</div>
""".strip()

    # Sort newest first.
    items = sorted(
        items,
        key=lambda announcement: announcement["date"],
        reverse=True,
    )

    html = []

    html.append('<div class="course-announcements-page">')

    html.append('<header class="course-announcements-header">')

    html.append(
        '<div class="course-announcements-label">'
        'Announcements'
        '</div>'
    )

    html.append('<h1>Training updates</h1>')

    if intro:
        html.append(
            '<p class="course-announcements-intro">'
            f'{intro}'
            '</p>'
        )

    html.append('</header>')

    html.append('<main class="course-announcements-list">')

    for announcement in items:

        announcement_date = announcement["date"]

        if isinstance(announcement_date, date):

            formatted_date = announcement_date.strftime(
                "%-d %B %Y"
            )

        else:

            formatted_date = str(announcement_date)

        html.append(
            '<article class="course-announcement-page-item">'
        )

        html.append(
            '<div class="course-announcement-page-date">'
            f'{formatted_date}'
            '</div>'
        )

        html.append(
            '<h2 class="course-announcement-page-title">'
            f'{announcement["title"]}'
            '</h2>'
        )

        html.append(
            '<p class="course-announcement-page-text">'
            f'{announcement["text"]}'
            '</p>'
        )

        html.append('</article>')

    html.append('</main>')

    html.append('</div>')

    return "\n".join(html).strip()