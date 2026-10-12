def render_footer(website):

    footer = website.get("footer", {})

    organisation = footer.get(
        "organisation",
        "",
    )

    licence = footer.get(
        "licence",
        {},
    )

    licence_name = licence.get("name")
    licence_url = licence.get("url")

    built_with = footer.get(
        "built_with",
        {},
    )

    repository = footer.get(
        "repository",
        {},
    )

    repository_url = repository.get("url")
    repository_image = repository.get("image")
    repository_alt = repository.get(
        "alt",
        "",
    )

    html = []

    html.append(
        '<div class="landing-footer">'
    )

    html.append(
        '<div class="landing-footer__meta">'
    )

    if organisation or licence_name:

        html.append("<p>")

        if organisation:
            html.append(
                f"By {organisation}"
            )

        if licence_name:

            if organisation:
                html.append(
                    ". Licensed under "
                )
            else:
                html.append(
                    "Licensed under "
                )

            if licence_url:
                html.append(
                    f'<a href="{licence_url}">'
                    f'{licence_name}'
                    "</a>"
                )
            else:
                html.append(
                    licence_name
                )

            html.append(".")

        html.append("</p>")

    if built_with:

        built_with_text = built_with.get("text", "")
        template_name = built_with.get("template_name", "")
        template_url = built_with.get("template_url", "")
        suffix = built_with.get("suffix", "")

        html.append("<p>")

        if built_with_text:
            html.append(
                f"{built_with_text} "
            )

        if template_name:

            if template_url:
                html.append(
                    f'<a href="{template_url}">'
                    f'{template_name}'
                    "</a>"
                )
            else:
                html.append(template_name)

        if suffix:
            html.append(
                f" {suffix}"
            )

        html.append("</p>")

    html.append("</div>")

    if repository_url and repository_image:

        html.append(
            '<div class="landing-footer__actions">'
        )

        html.append(
            f'<a href="{repository_url}" '
            'class="landing-footer__image-link">'
        )

        html.append(
            f'<img src="{repository_image}" '
            f'alt="{repository_alt}" '
            'class="landing-footer__image">'
        )

        html.append("</a>")
        html.append("</div>")

    html.append("</div>")

    return "".join(html).strip()