"""
The footer of the landing page.

Most of the footer comes from the other data files, so nothing needs to
be filled in twice:

- the organisation(s): "organizers" in data/course.yml;
- the licence: "reuse.licence" and "reuse.licence_url" in
  data/course.yml;
- the repository link: the GitHub address of this repository, worked
  out automatically (see fair.repository_url).

Only the "built with" text and the repository icon are set in the
footer part of data/website.yml.
"""

from html import escape

from renderers import fair


def _join(names):
    """Join names as "A", "A and B" or "A, B and C"."""

    if len(names) <= 1:
        return "".join(names)

    return ", ".join(names[:-1]) + " and " + names[-1]


def _link(text, url):
    """Return a link, or plain text when there is no URL."""

    if url:
        return f'<a href="{escape(url, quote=True)}">{escape(text)}</a>'

    return escape(text)


def render_footer(website, course):
    """
    Return the footer HTML.

    course is the course data described by the website: data/course.yml,
    or the template's own _template/course.yml in template mode.
    """

    footer = website.get("footer") or {}

    organisation = _join([
        " ".join(str(name).split())
        for name in course.get("organizers") or []
        if str(name or "").strip()
    ])

    reuse = course.get("reuse") or {}
    licence_name = " ".join(str(reuse.get("licence") or "").split())
    licence_url = fair.licence_url(course)

    built_with = footer.get("built_with") or {}

    repository = footer.get("repository") or {}
    repository_url = fair.repository_url(website)
    repository_image = repository.get("image")
    repository_alt = repository.get("alt", "")

    html = ['<div class="landing-footer">', '<div class="landing-footer__meta">']

    if organisation or licence_name:
        parts = []

        if organisation:
            parts.append(f"By {escape(organisation)}.")

        if licence_name:
            parts.append(f"Licensed under {_link(licence_name, licence_url)}.")

        html.append(f"<p>{' '.join(parts)}</p>")

    if built_with:
        text = built_with.get("text", "")
        template_name = built_with.get("template_name", "")
        template_url = built_with.get("template_url", "")
        suffix = built_with.get("suffix", "")

        parts = [
            escape(text) if text else "",
            _link(template_name, template_url) if template_name else "",
            escape(suffix) if suffix else "",
        ]

        html.append(f"<p>{' '.join(part for part in parts if part)}</p>")

    html.append("</div>")

    if repository_url and repository_image:
        html.append(
            '<div class="landing-footer__actions">'
            f'<a href="{escape(repository_url, quote=True)}" '
            'class="landing-footer__image-link">'
            f'<img src="{escape(str(repository_image), quote=True)}" '
            f'alt="{escape(str(repository_alt), quote=True)}" '
            'class="landing-footer__image">'
            "</a>"
            "</div>"
        )

    html.append("</div>")

    return "".join(html)
