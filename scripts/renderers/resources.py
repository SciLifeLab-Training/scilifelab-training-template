from html import escape


def render_resources(resources):

    if not resources:
        return ""

    sections = [
        (
            "further_reading",
            "Further reading",
            "Books, papers, articles, reviews, and other material for deeper learning after the training.",
            "book",
        ),
        (
            "useful_links",
            "Useful links",
            "Relevant websites, portals, communities, organisations, or other online resources.",
            "link-45deg",
        ),
        (
            "documentation_and_tutorials",
            "Documentation and tutorials",
            "Documentation, guides, tutorials, walkthroughs, and other practical learning resources.",
            "file-earmark-text",
        ),
        (
            "tools_and_software",
            "Tools and software",
            "Software, packages, platforms, applications, or other tools that participants may want to continue using.",
            "laptop",
        ),
        (
            "datasets",
            "Datasets",
            "Public datasets, repositories, example datasets, or other data resources for further practice.",
            "database",
        ),
        (
            "related_training",
            "Related training",
            "Other courses, workshops, training materials, or learning opportunities related to this training.",
            "mortarboard",
        ),
    ]

    html = []

    html.append('<div class="course-resources-page">')

    html.append('<header class="course-resources-header">')

    html.append('<div class="course-page-label">Resources</div>')

    html.append('<h1 class="course-page-title">Explore further after the training</h1>')

    if resources.get("intro"):
        html.append(
            '<p class="course-page-intro">'
            f'{escape(str(resources["intro"]))}'
            '</p>'
        )

    html.append('</header>')

    for key, title, description, icon in sections:

        items = resources.get(key) or []

        if not items:
            continue

        html.append('<section class="course-resources-section">')

        html.append('<div class="course-resources-section-header">')

        html.append(
            '<div class="course-resources-section-icon">'
            f'<i class="bi bi-{icon}"></i>'
            '</div>'
        )

        html.append('<div class="course-resources-section-heading">')

        html.append(
            f'<h2>{escape(title)}</h2>'
        )

        html.append(
            f'<p>{escape(description)}</p>'
        )

        html.append('</div>')

        html.append('</div>')

        html.append('<div class="course-resources-list">')

        for item in items:

            item_title = escape(
                str(item.get("title", ""))
            )

            item_description = escape(
                str(item.get("description", ""))
            )

            item_url = escape(
                str(item.get("url", "")),
                quote=True,
            )

            html.append(
                '<div class="course-resource">'
            )

            html.append(
                '<div class="course-resource-content">'
            )

            html.append(
                f'<h3>{item_title}</h3>'
            )

            if item_description:
                html.append(
                    f'<p>{item_description}</p>'
                )

            html.append('</div>')

            if item_url:
                html.append(
                    '<a '
                    'class="course-resource-link course-text-link" '
                    f'href="{item_url}" '
                    'target="_blank" '
                    'rel="noopener">'
                    'View resource '
                    '<i class="bi bi-box-arrow-up-right"></i>'
                    '</a>'
                )

            html.append('</div>')

        html.append('</div>')

        html.append('</section>')

    html.append('</div>')

    return "\n".join(html).strip()