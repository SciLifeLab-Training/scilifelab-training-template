from utils import format_date


def render_welcome(course, website):

    title = course["title"]

    start = course.get("start_date")
    end = course.get("end_date")
    location = course.get("location")

    welcome = website.get("welcome", {})

    welcome_title = welcome.get(
        "title",
        "Welcome to the training",
    )

    welcome_text = welcome.get(
        "text",
        "",
    )

    image = welcome.get(
        "image",
        {},
    )

    image_src = image.get(
        "src",
        "",
    )

    image_alt = image.get(
        "alt",
        "",
    )

    meta = []

    if start and end:
        meta.append(f"""
<span class="course-welcome-item">
<i class="bi bi-calendar2-event"></i>
{format_date(start)} – {format_date(end)}
</span>
""")

    elif start:
        meta.append(f"""
<span class="course-welcome-item">
<i class="bi bi-calendar2-event"></i>
{format_date(start)}
</span>
""")

    elif end:
        meta.append(f"""
<span class="course-welcome-item">
<i class="bi bi-calendar2-event"></i>
{format_date(end)}
</span>
""")

    if location:
        meta.append(f"""
<span class="course-welcome-item">
<i class="bi bi-geo-alt"></i>
{location}
</span>
""")

    html = []

    html.append(
        '<div class="course-welcome-text">'
    )

    html.append(
        f"# {title}"
    )

    if meta:
        html.append(
            '<div class="course-welcome-meta">'
            + "".join(meta)
            + "</div>"
        )

    if welcome_title:
        html.append(
            f"## {welcome_title}"
        )

    if welcome_text:
        html.append(
            welcome_text
        )

    html.append("</div>")

    if image_src:

        html.append(
            '<div class="course-welcome-image">'
        )

        html.append(
            f'<img src="{image_src}" alt="{image_alt}" class="course-welcome-graphic">'
        )

        html.append("</div>")

    return "\n\n".join(html).strip()