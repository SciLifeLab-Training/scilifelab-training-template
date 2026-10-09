from utils import format_date
from renderers.fair import (
    concept_doi,
    version_doi,
    citation_text,
    funding,
)


def render_syllabus(course, team, website):

    # ---------------------------------------------------------
    # Syllabus header
    # ---------------------------------------------------------

    html = []

    html.append('<div class="course-syllabus-header">')
    html.append('<div class="course-syllabus-header-main">')
    html.append('<div class="course-page-label">Syllabus</div>')
    html.append(f'<h1 class="course-page-title">{course["title"]}</h1>')

    if course.get("subtitle"):
        html.append(
            f'<p class="course-page-intro">{course["subtitle"]}</p>'
        )

    html.append('</div>')

    html.append('</div>')

    # ---------------------------------------------------------
    # Syllabus content
    # ---------------------------------------------------------

    html.append('<div class="course-syllabus">')

    # ---------------------------------------------------------
    # Training overview
    # ---------------------------------------------------------

    html.append('<section class="course-syllabus-section">')
    html.append('<h2>Abstract</h2>')
    html.append(f'<p>{course["description"]}</p>')

    keywords = [
        keyword
        for keyword in course.get("keywords", [])
        if keyword
    ]

    if keywords:
        html.append(
            '<p class="course-syllabus-keywords">'
            '<strong>Keywords:</strong> '
            + ' · '.join(keywords)
            + '</p>'
        )

    html.append('</section>')

    # ---------------------------------------------------------
    # Training details
    # ---------------------------------------------------------

    details = []

    if course.get("start_date") and course.get("end_date"):
        details.append(
            (
                "Dates",
                f'{format_date(course["start_date"])} – '
                f'{format_date(course["end_date"])}'
            )
        )

    elif course.get("start_date"):
        details.append(
            ("Start date", format_date(course["start_date"]))
        )

    elif course.get("end_date"):
        details.append(
            ("End date", format_date(course["end_date"]))
        )

    if course.get("duration"):
        details.append(
            ("Duration", course["duration"])
        )

    if course.get("mode"):
        details.append(
            ("Delivery", course["mode"])
        )

    if course.get("location"):
        details.append(
            ("Location", course["location"])
        )

    if course.get("language"):
        details.append(
            ("Language", course["language"])
        )

    credits = course.get("credits")

    if credits:
        value = credits.get("value")
        unit = credits.get("unit", "")
        note = credits.get("note")

        if value is not None:
            credit_value = f"{value} {unit}".strip()

            if note:
                credit_value += (
                    '<br>'
                    f'<span class="course-syllabus-note">{note}</span>'
                )

            details.append(
                ("Credits", credit_value)
            )

    if details:
        html.append('<section class="course-syllabus-section">')
        html.append('<h2>Details</h2>')
        html.append('<dl class="course-syllabus-details">')

        for label, value in details:
            html.append(
                '<div>'
                f'<dt>{label}</dt>'
                f'<dd>{value}</dd>'
                '</div>'
            )

        html.append('</dl>')
        html.append('</section>')

    # ---------------------------------------------------------
    # Learning outcomes
    # ---------------------------------------------------------

    outcomes = [
        outcome
        for outcome in course.get("learning_outcomes", [])
        if outcome
    ]

    if outcomes:
        html.append('<section class="course-syllabus-section">')
        html.append('<h2>Learning outcomes</h2>')
        html.append(
            '<p>'
            'After completing this training, participants will be able to:'
            '</p>'
        )

        html.append('<ol class="course-syllabus-outcomes">')

        for outcome in outcomes:
            html.append(
                '<li>'
                '<span class="course-syllabus-outcome-number"></span>'
                f'<span class="course-syllabus-outcome-text">{outcome}</span>'
                '</li>'
            )

        html.append('</ol>')
        html.append('</section>')

    # ---------------------------------------------------------
    # Target audience
    # ---------------------------------------------------------

    if (
        course.get("target_audience")
        or course.get("expertise_level")
    ):
        html.append('<section class="course-syllabus-section">')
        html.append('<h2>Target audience</h2>')

        if course.get("target_audience"):
            html.append(
                f'<p>{course["target_audience"]}</p>'
            )

        if course.get("expertise_level"):
            html.append(
                '<p>'
                '<strong>Expertise level:</strong> '
                f'{course["expertise_level"]}'
                '</p>'
            )

        html.append('</section>')

    # ---------------------------------------------------------
    # Prerequisites
    # ---------------------------------------------------------

    prerequisites = course.get("prerequisites", {})

    knowledge = [
        item
        for item in prerequisites.get("knowledge", [])
        if item
    ]

    technical = [
        item
        for item in prerequisites.get("technical", [])
        if item
    ]

    if knowledge or technical:
        html.append('<section class="course-syllabus-section">')
        html.append('<h2>Prerequisites</h2>')
        html.append('<div class="course-syllabus-columns">')

        if knowledge:
            html.append('<div class="course-syllabus-column">')
            html.append('<h3>Knowledge</h3>')
            html.append('<ul>')

            for item in knowledge:
                html.append(f'<li>{item}</li>')

            html.append('</ul>')
            html.append('</div>')

        if technical:
            html.append('<div class="course-syllabus-column">')
            html.append('<h3>Technical</h3>')
            html.append('<ul>')

            for item in technical:
                html.append(f'<li>{item}</li>')

            html.append('</ul>')
            html.append('</div>')

        html.append('</div>')
        html.append('</section>')

    # ---------------------------------------------------------
    # Forms of instruction and examination
    # ---------------------------------------------------------

    instruction = [
        item
        for item in course.get("instruction", [])
        if item
    ]

    examination = course.get("examination", {})
    examination_description = examination.get("description")

    if instruction or examination_description:
        html.append('<section class="course-syllabus-section">')
        html.append(
            '<h2>Forms of instruction and examination</h2>'
        )
        html.append('<div class="course-syllabus-columns">')

        if instruction:
            html.append('<div class="course-syllabus-column">')
            html.append('<h3>Forms of instruction</h3>')
            html.append('<ul>')

            for item in instruction:
                html.append(f'<li>{item}</li>')

            html.append('</ul>')
            html.append('</div>')

        if examination_description:
            html.append('<div class="course-syllabus-column">')
            html.append('<h3>Forms of examination</h3>')
            html.append(
                f'<p>{examination_description}</p>'
            )
            html.append('</div>')

        html.append('</div>')
        html.append('</section>')

    # ---------------------------------------------------------
    # Administration
    # ---------------------------------------------------------

    organizers = [
        organizer
        for organizer in course.get("organizers", [])
        if organizer
    ]

    content_providers = [
        provider
        for provider in course.get("content_providers", [])
        if provider
    ]

    # Each funder is shown with its grant title and number, if given.
    funders = []

    for entry in funding(course):
        text = entry["funder"]

        if entry["grant_title"]:
            text += f', {entry["grant_title"]}'

        if entry["grant_number"]:
            text += f' (grant {entry["grant_number"]})'

        funders.append(text)

    team_members = team.get("members") or []

    leaders = [
        person
        for person in team_members
        if "Training lead" in person.get("roles", [])
    ]

    if organizers or content_providers or funders or leaders:
        html.append('<section class="course-syllabus-section">')
        html.append('<h2>Administration</h2>')
        html.append('<div class="course-syllabus-columns">')

        if organizers or content_providers or funders:
            html.append('<div class="course-syllabus-column">')

            if organizers:
                html.append(
                    '<h3>Organising organisation(s)</h3>'
                )
                html.append('<ul>')

                for organizer in organizers:
                    html.append(f'<li>{organizer}</li>')

                html.append('</ul>')

            if content_providers:
                html.append(
                    '<h3>Content provider(s)</h3>'
                )
                html.append('<ul>')

                for provider in content_providers:
                    html.append(f'<li>{provider}</li>')

                html.append('</ul>')

            if funders:
                html.append(
                    '<h3>Funder(s)</h3>'
                )
                html.append('<ul>')

                for funder in funders:
                    html.append(f'<li>{funder}</li>')

                html.append('</ul>')

            html.append('</div>')

        if leaders:
            html.append('<div class="course-syllabus-column">')
            html.append('<h3>Team lead(s)</h3>')
            html.append('<div class="course-syllabus-leaders">')

            for leader in leaders:
                html.append('<div class="course-syllabus-leader">')
                html.append(
                    f'<strong>{leader["name"]}</strong>'
                )

                if leader.get("affiliation"):
                    html.append(
                        f'<span>{leader["affiliation"]}</span>'
                    )

                if leader.get("email"):
                    html.append(
                        f'<a class="course-text-link" href="mailto:{leader["email"]}">'
                        f'{leader["email"]}'
                        '</a>'
                    )

                html.append('</div>')

            html.append('</div>')
            html.append('</div>')

        html.append('</div>')
        html.append('</section>')

    # ---------------------------------------------------------
    # Reuse
    # ---------------------------------------------------------

    reuse = course.get("reuse", {})

    licence = reuse.get("licence")
    licence_url = reuse.get("licence_url")
    doi = version_doi(course) or concept_doi(course)
    doi_url = f"https://doi.org/{doi}" if doi else ""
    preferred_citation = citation_text(course, team, website)

    if licence or doi or preferred_citation:
        html.append(
            '<section class="course-syllabus-section">'
        )
        html.append('<h2>Reuse</h2>')
        html.append(
            '<dl class="course-syllabus-details course-syllabus-reuse">'
        )

        if licence:
            licence_html = licence

            if licence_url:
                licence_html = (
                    f'<a class="course-text-link" href="{licence_url}" '
                    f'target="_blank" rel="noopener">'
                    f'{licence}</a>'
                )

            html.append(
                '<div>'
                '<dt>Licence</dt>'
                f'<dd>{licence_html}</dd>'
                '</div>'
            )

        if doi:
            doi_html = doi

            if doi_url:
                doi_html = (
                    f'<a class="course-text-link" href="{doi_url}" '
                    f'target="_blank" rel="noopener">'
                    f'{doi}</a>'
                )

            html.append(
                '<div>'
                '<dt>DOI</dt>'
                f'<dd>{doi_html}</dd>'
                '</div>'
            )

        if preferred_citation:
            html.append(
                '<div class="course-syllabus-preferred-citation">'
                '<dt>Preferred citation</dt>'
                f'<dd>{preferred_citation}</dd>'
                '</div>'
            )

        html.append('</dl>')
        html.append('</section>')

    # ---------------------------------------------------------
    # Close syllabus content
    # ---------------------------------------------------------

    html.append('</div>')

    # ---------------------------------------------------------
    # Final output
    # ---------------------------------------------------------

    return "\n".join(html)