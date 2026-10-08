from html import escape

import re


# ---------------------------------------------------------
# Small helpers
# ---------------------------------------------------------

def _text(value):

    """Return safely escaped single-line text."""

    if value is None:

        return ""

    return escape(str(value))


def _multiline(value):
    """
    Render multiline YAML text as HTML paragraphs/line breaks.

    Blank lines create separate paragraphs.

    Single newlines are preserved as line breaks.
    """

    if not value:

        return ""

    value = str(value).strip()

    if not value:

        return ""

    paragraphs = []

    for paragraph in value.split("\n\n"):

        paragraph = paragraph.strip()

        if not paragraph:

            continue

        paragraph = escape(paragraph)

        paragraph = paragraph.replace("\n", "<br>")

        paragraphs.append(
            f"<p>{paragraph}</p>"
        )

    return "\n".join(paragraphs)


def _link(link):

    """Render a single link."""

    if not link:

        return ""

    title = link.get("title")

    url = link.get("url")

    if not title or not url:

        return ""

    return (
        '<a class="course-text-link" '
        f'href="{escape(str(url), quote=True)}" '
        'target="_blank" '
        'rel="noopener">'
        f'{_text(title)}'
        '</a>'
    )


def _links(links):

    """Render a list of links."""

    valid_links = [
        link
        for link in (links or [])
        if link and link.get("title") and link.get("url")
    ]

    if not valid_links:

        return ""

    html = []

    html.append('<ul class="course-preparation-links">')

    for link in valid_links:

        html.append("<li>")

        html.append(_link(link))

        html.append("</li>")

    html.append("</ul>")

    return "\n".join(html)


def _instructions(value):

    """Render an instructions block with paragraphs and ordered lists."""

    if not value:

        return ""

    value = str(value).strip()

    if not value:

        return ""

    html = []

    html.append(
        '<div class="course-preparation-instructions">'
    )

    html.append("<h4>Instructions</h4>")

    paragraph_lines = []

    list_items = []

    current_item = None

    def flush_paragraph():

        if not paragraph_lines:

            return

        text = " ".join(
            line.strip()
            for line in paragraph_lines
        )

        html.append(
            f"<p>{_text(text)}</p>"
        )

        paragraph_lines.clear()

    def flush_list():

        nonlocal current_item

        if current_item is not None:

            list_items.append(current_item)

            current_item = None

        if not list_items:

            return

        html.append("<ol>")

        for item in list_items:

            html.append(
                f"<li>{_text(item)}</li>"
            )

        html.append("</ol>")

        list_items.clear()

    for line in value.splitlines():

        line = line.strip()

        # Blank line: finish the current paragraph/list.
        if not line:

            if current_item is not None:

                flush_list()

            else:

                flush_paragraph()

            continue

        # Numbered list item.
        match = re.match(r"^\d+\.\s+(.*)$", line)

        if match:

            flush_paragraph()

            if current_item is not None:

                list_items.append(current_item)

            current_item = match.group(1)

            continue

        # Continuation of the current list item.
        if current_item is not None:

            current_item += f" {line}"

            continue

        # Ordinary paragraph text.
        paragraph_lines.append(line)

    # Flush anything remaining.
    if current_item is not None:

        flush_list()

    else:

        flush_paragraph()

    html.append("</div>")

    return "\n".join(html)


# ---------------------------------------------------------
# Generic box helpers
# ---------------------------------------------------------

def _box_header(title, icon):

    """Render the grey header used by standard preparation boxes."""

    if not title:

        return ""

    return "\n".join(
        [
            '<div class="course-preparation-box-header">',
            f'<i class="bi {icon} course-preparation-box-icon"></i>',
            '<h3 class="course-preparation-box-title">',
            _text(title),
            '</h3>',
            '</div>',
        ]
    )


def _box_start(class_name):

    """Start a standard preparation box."""

    return f'<div class="course-preparation-box {class_name}">'


def _box_body_start():

    """Start the white body of a standard preparation box."""

    return '<div class="course-preparation-box-body">'


def _box_end():

    """Close a standard preparation box."""

    return "</div>"


# ---------------------------------------------------------
# Block renderers
# ---------------------------------------------------------

def _render_text(block):

    content = block.get("content")

    if not content:

        return ""

    html = []

    html.append('<div class="course-preparation-text">')

    html.append(_multiline(content))

    html.append("</div>")

    return "\n".join(html)


def _render_callout(block):

    style = block.get("style", "note")

    title = block.get("title")

    content = block.get("content")

    if not content and not title:

        return ""

    if style == "warning":

        icon = "bi-exclamation-triangle"

    elif style == "note":

        icon = "bi-sticky"

    else:

        icon = "bi-info-circle"

    html = []

    html.append(
        f'<div class="course-preparation-callout '
        f'course-preparation-callout-{escape(str(style))}">'
    )

    if title:

        html.append(
            '<div class="course-preparation-callout-title">'
        )

        html.append(
            f'<i class="bi {icon} '
            'course-preparation-callout-icon"></i>'
        )

        html.append(_text(title))

        html.append("</div>")

    if content:

        html.append(
            '<div class="course-preparation-callout-content">'
        )

        html.append(_multiline(content))

        html.append("</div>")

    html.append("</div>")

    return "\n".join(html)


def _render_checklist(block):

    title = block.get("title")

    items = [
        item
        for item in (block.get("items") or [])
        if item
    ]

    if not title and not items:

        return ""

    html = []

    html.append(
        _box_start("course-preparation-checklist")
    )

    if title:

        html.append(
            _box_header(
                title,
                "bi-check2-square",
            )
        )

    html.append(_box_body_start())

    if items:

        html.append("<ul>")

        for item in items:

            html.append(
                "<li>"
                "<label>"
                '<input type="checkbox" '
                'class="course-preparation-checkbox">'
                f"<span>{_text(item)}</span>"
                "</label>"
                "</li>"
            )

        html.append("</ul>")

    html.append(_box_end())

    html.append(_box_end())

    return "\n".join(html)


def _render_account(block):

    title = block.get("title")

    description = block.get("description")

    instructions = block.get("instructions")

    links = block.get("links") or []

    if not title and not description and not instructions and not links:

        return ""

    html = []

    html.append(
        _box_start("course-preparation-account")
    )

    if title:

        html.append(
            _box_header(
                title,
                "bi-person-badge",
            )
        )

    html.append(_box_body_start())

    if description:

        html.append(
            '<div class="course-preparation-resource-description">'
        )

        html.append(_multiline(description))

        html.append("</div>")

    if instructions:

        html.append(_instructions(instructions))

    if links:

        html.append(_links(links))

    html.append(_box_end())

    html.append(_box_end())

    return "\n".join(html)


def _render_account_grid(blocks):

    """Render consecutive account blocks as a two-column grid."""

    rendered = []

    for block in blocks:

        account = _render_account(block)

        if account:

            rendered.append(account)

    if not rendered:

        return ""

    html = []

    html.append(
        '<div class="course-preparation-account-grid">'
    )

    html.extend(rendered)

    html.append("</div>")

    return "\n".join(html)


def _render_software_grid(blocks):

    """Render consecutive software blocks as a two-column grid."""

    rendered = []

    for block in blocks:

        software = _render_software(block)

        if software:

            rendered.append(software)

    if not rendered:

        return ""

    html = []

    html.append(
        '<div class="course-preparation-software-grid">'
    )

    html.extend(rendered)

    html.append("</div>")

    return "\n".join(html)


def _render_hardware(block):

    title = block.get("title")

    description = block.get("description")

    requirements = block.get("requirements") or []

    instructions = block.get("instructions")

    if not title and not description and not requirements and not instructions:

        return ""

    html = []

    html.append(
        _box_start("course-preparation-hardware")
    )

    if title:

        html.append(
            _box_header(
                title,
                "bi-laptop",
            )
        )

    html.append(_box_body_start())

    if description:

        html.append(
            '<div class="course-preparation-resource-description">'
        )

        html.append(_multiline(description))

        html.append("</div>")

    valid_requirements = [
        requirement
        for requirement in requirements
        if requirement
        and requirement.get("label")
        and requirement.get("value")
    ]

    if valid_requirements:

        html.append(
            '<dl class="course-preparation-requirements">'
        )

        for requirement in valid_requirements:

            html.append("<div>")

            html.append(
                f'<dt>{_text(requirement["label"])}</dt>'
            )

            html.append(
                f'<dd>{_text(requirement["value"])}</dd>'
            )

            html.append("</div>")

        html.append("</dl>")

    if instructions:

        html.append(_instructions(instructions))

    html.append(_box_end())

    html.append(_box_end())

    return "\n".join(html)


def _render_software(block):

    title = block.get("title")

    description = block.get("description")

    instructions = block.get("instructions")

    links = block.get("links") or []

    if not title and not description and not instructions and not links:

        return ""

    html = []

    html.append(
        _box_start("course-preparation-software")
    )

    if title:

        html.append(
            _box_header(
                title,
                "bi-download",
            )
        )

    html.append(_box_body_start())

    if description:

        html.append(
            '<div class="course-preparation-resource-description">'
        )

        html.append(_multiline(description))

        html.append("</div>")

    if instructions:

        html.append(_instructions(instructions))

    if links:

        html.append(_links(links))

    html.append(_box_end())

    html.append(_box_end())

    return "\n".join(html)


def _render_reading(block):

    title = block.get("title")

    description = block.get("description")

    citations = block.get("citations") or []

    instructions = block.get("instructions")

    prompt = block.get("prompt")

    links = block.get("links") or []

    if not any(
        [
            title,
            description,
            citations,
            instructions,
            prompt,
            links,
        ]
    ):

        return ""

    html = []

    html.append(
        _box_start("course-preparation-reading")
    )

    if title:

        html.append(
            _box_header(
                title,
                "bi-book",
            )
        )

    html.append(_box_body_start())

    if description:

        html.append(
            '<div class="course-preparation-resource-description">'
        )

        html.append(_multiline(description))

        html.append("</div>")

    if citations:

        valid_citations = [
            citation
            for citation in citations
            if citation
        ]

        if valid_citations:

            html.append(
                '<div class="course-preparation-citations">'
            )

            for citation in valid_citations:

                if isinstance(citation, dict):

                    text = citation.get("text", "")

                    url = citation.get("url", "")

                else:

                    text = str(citation)

                    url = ""

                if not text:

                    continue

                html.append(
                    '<div class="course-preparation-citation">'
                )

                html.append("<p>")

                if url:
                    html.append(
                        f'<a href="{escape(str(url), quote=True)}" '
                        'target="_blank" '
                        'rel="noopener noreferrer">'
                    )

                html.append(_text(text))

                if url:
                    html.append("</a>")

                html.append("</p>")
                html.append("</div>")

            html.append("</div>")

    if instructions:

        html.append(_instructions(instructions))

    if prompt:

        html.append(
            '<div class="course-preparation-prompt">'
        )

        html.append(
            '<div class="course-preparation-prompt-title">'
        )

        html.append(
            '<i class="bi bi-question-circle"></i>'
        )

        html.append("Reflection prompt")

        html.append("</div>")

        html.append(_multiline(prompt))

        html.append("</div>")

    if links:

        html.append(_links(links))

    html.append(_box_end())

    html.append(_box_end())

    return "\n".join(html)


def _render_block(block):

    """Render one preparation block according to its type."""

    if not block:

        return ""

    block_type = block.get("type")

    renderers = {
        "text": _render_text,
        "callout": _render_callout,
        "checklist": _render_checklist,
        "account": _render_account,
        "hardware": _render_hardware,
        "software": _render_software,
        "reading": _render_reading,
    }

    renderer = renderers.get(block_type)

    if renderer is None:

        return ""

    return renderer(block)


# ---------------------------------------------------------
# Main renderer
# ---------------------------------------------------------

def render_preparation(preparation, course):

    """
    Render the complete Preparation page.

    The returned value is Quarto-compatible HTML embedded
    in the generated .qmd file.
    """

    if not preparation:

        return ""

    sections = preparation.get("sections") or []

    if not sections:

        return ""

    html = []

    # -----------------------------------------------------
    # Page header
    # -----------------------------------------------------

    html.append(
        '<div class="course-preparation-header">'
    )

    html.append(
        '<div class="course-preparation-header-main">'
    )

    html.append(
        '<div class="course-page-label">'
        'Preparation'
        '</div>'
    )

    html.append(
        '<h1 class="course-page-title">Prepare for the training</h1>'
    )

    if preparation.get("intro"):

        html.append(
            '<p class="course-page-intro course-page-intro-narrow">'
            f'{_text(preparation["intro"])}'
            '</p>'
        )

    html.append("</div>")

    contact = course.get("contact", {})

    contact_email = contact.get("email")

    if contact_email:

        html.append(
            '<div class="course-page-contact">'
        )

        html.append(
            '<div class="course-page-contact-icon">'
            '<i class="bi bi-envelope"></i>'
            '</div>'
        )

        html.append(
            '<div class="course-page-contact-title">'
            'Questions about the training?'
            '</div>'
        )

        html.append(
            "<p>Get in touch with the training team.</p>"
        )

        html.append(
            f'<a class="course-text-link" href="mailto:{contact_email}">'
            f'{contact_email}'
            '</a>'
        )

        html.append("</div>")

    html.append("</div>")

    # -----------------------------------------------------
    # Page content
    # -----------------------------------------------------

    html.append(
        '<div class="course-preparation">'
    )

    for section in sections:

        if not section:

            continue

        title = section.get("title")

        blocks = section.get("blocks") or []

        # -------------------------------------------------
        # Render blocks
        # -------------------------------------------------

        rendered_blocks = []

        i = 0

        while i < len(blocks):

            block = blocks[i]

            if not block:

                i += 1

                continue

            # Group consecutive account blocks into a grid.
            if block.get("type") == "account":

                account_blocks = []

                while (
                    i < len(blocks)
                    and blocks[i]
                    and blocks[i].get("type") == "account"
                ):

                    account_blocks.append(blocks[i])

                    i += 1

                rendered = _render_account_grid(
                    account_blocks
                )

            elif block.get("type") == "software":

                software_blocks = []

                while (
                    i < len(blocks)
                    and blocks[i]
                    and blocks[i].get("type") == "software"
                ):

                    software_blocks.append(blocks[i])

                    i += 1

                rendered = _render_software_grid(
                    software_blocks
                )

            else:

                rendered = _render_block(block)

                i += 1

            if rendered:

                rendered_blocks.append(rendered)

        # Ignore completely empty sections.
        if not rendered_blocks:

            continue

        # -------------------------------------------------
        # Section
        # -------------------------------------------------

        html.append(
            '<section class="course-preparation-section">'
        )

        if title:

            html.append(
                "<h2>"
                f'{_text(title)}'
                "</h2>"
            )

        html.extend(rendered_blocks)

        html.append("</section>")

    html.append("</div>")

    return "\n".join(html)