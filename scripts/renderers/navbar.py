from html import escape


def render_navbar_meta(course):
    title = course["title"]

    return f"""
<h1>{title}</h1>
""".strip()


def render_navbar_brand(website, content_page=False):
    logos = website["navbar"]["logos"]

    # Keep the primary logo last so it appears on the right.
    logos = sorted(
        logos,
        key=lambda logo: bool(logo.get("primary", False)),
    )

    html = []

    for logo in logos:
        src = escape(str(logo["src"]), quote=True)
        alt = escape(str(logo["alt"]), quote=True)
        height = int(logo.get("height", 46))

        if height <= 0:
            raise ValueError(
                f"Logo height must be a positive number. Got: {height}"
            )

        if content_page:
            image_source = f'src="" data-course-asset="{src}"'
        else:
            image_source = f'src="{src}"'

        # The primary logo gets a compact mobile variant.
        if logo.get("primary", False):
            compact_src = "img/scilifelab-logo-neg.png"
            compact_src = escape(compact_src, quote=True)

            if content_page:
                compact_image_source = (
                    f'src="" data-course-asset="{compact_src}"'
                )
            else:
                compact_image_source = f'src="{compact_src}"'

            html.append(
                f'<img {image_source} '
                f'alt="{alt}" '
                f'class="course-navbar-logo course-navbar-logo-full" '
                f'style="height: {height}px; width: auto;">'
            )

            html.append(
                f'<img {compact_image_source} '
                f'alt="" '
                f'class="course-navbar-logo course-navbar-logo-symbol" '
                f'style="height: {height}px; width: auto;">'
            )

        else:
            html.append(
                f'<img {image_source} '
                f'alt="{alt}" '
                f'class="course-navbar-logo" '
                f'style="height: {height}px; width: auto;">'
            )

    return "\n".join(html)


def render_navbar_links(website, available_pages):
    links = [
        ("Overview", "index.qmd"),
        ("Content", "content/index.qmd"),
    ]

    # Schedule is optional.
    if "schedule" in available_pages:
        links.append(("Schedule", "schedule.qmd"))

    html = []

    # Main navigation links.
    for title, page in links:
        href = page.replace(".qmd", ".html")

        html.append(
            f'<a class="course-navbar-link" '
            f'href="{href}" '
            f'data-page="{page}">'
            f'{title}'
            '</a>'
        )

    # Course information dropdown.
    dropdown_links = [
        ("Preparation", "preparation.qmd", "preparation"),
        ("Practicalities", "practicalities.qmd", "practicalities"),
        ("Announcements", "announcements.qmd", "announcements"),
        ("Resources", "resources.qmd", "resources"),
        ("Team", "team.qmd", True),
        ("Syllabus", "syllabus.qmd", True),
        ("FAQ", "faq.qmd", "faq"),
    ]

    available_dropdown_links = []

    for title, page, availability in dropdown_links:
        if availability is True:
            available = True
        else:
            available = availability in available_pages

        if available:
            available_dropdown_links.append((title, page))

    if available_dropdown_links:
        html.append('<div class="course-navbar-dropdown">')

        html.append(
            '<button class="course-navbar-link '
            'course-navbar-dropdown-toggle" '
            'type="button" '
            'aria-haspopup="true">'
            'Information'
            '<i class="bi bi-chevron-down '
            'course-navbar-dropdown-icon"></i>'
            '</button>'
        )

        html.append('<div class="course-navbar-dropdown-menu">')

        for title, page in available_dropdown_links:
            href = page.replace(".qmd", ".html")

            html.append(
                f'<a class="course-navbar-dropdown-link" '
                f'href="{href}" '
                f'data-page="{page}">'
                f'{title}'
                '</a>'
            )

        html.append('</div>')
        html.append('</div>')

    return "\n".join(html)