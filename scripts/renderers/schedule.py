from collections import OrderedDict

from utils import format_date


MONTHS = [
    "JAN", "FEB", "MAR", "APR",
    "MAY", "JUN", "JUL", "AUG",
    "SEP", "OCT", "NOV", "DEC",
]


def render_schedule(events, course):

    if not events:
        return ""

    # ------------------------------------------------------------------
    # Course metadata
    # ------------------------------------------------------------------

    start_date = course.get("start_date")
    end_date = course.get("end_date")
    location = course.get("location")

    start = format_date(start_date) if start_date else None
    end = format_date(end_date) if end_date else None

    if start and end:
        date_text = f"{start} – {end}"
    elif start:
        date_text = start
    elif end:
        date_text = end
    else:
        date_text = None

    meta = ""

    if date_text:
        meta += f"""
<span class="course-welcome-item">
<i class="bi bi-calendar2-event"></i>
{date_text}
</span>
"""

    if location:
        meta += f"""
<span class="course-welcome-item">
<i class="bi bi-geo-alt"></i>
{location}
</span>
"""

    page_header = f"""
<div class="course-page-header">

<h1>Schedule</h1>

<div class="course-page-meta">

{meta}

</div>

</div>
""".strip()


    # ------------------------------------------------------------------
    # Group events by course day
    # ------------------------------------------------------------------

    events = sorted(events, key=lambda event: event["start"])

    grouped = OrderedDict()

    for event in events:

        group = event["group"]

        if group not in grouped:
            grouped[group] = []

        grouped[group].append(event)

    sidebar = []
    timeline = []

    for group, day_events in grouped.items():

        first = day_events[0]["start"]

        weekday = first.strftime("%A")
        day = first.day
        month = MONTHS[first.month - 1].title()

        day_id = group.lower().replace(" ", "-")

        # --------------------------------------------------------------
        # Sidebar
        # --------------------------------------------------------------

        sidebar.append(
            f"""
<button
    type="button"
    class="course-schedule-day-link"
    data-day="{day_id}">

<div class="course-schedule-day-name">
{group}
</div>

<div class="course-schedule-day-date">
{weekday}, {month} {day}
</div>

</button>
"""
        )

        # --------------------------------------------------------------
        # Events
        # --------------------------------------------------------------

        rows = []

        for index, event in enumerate(day_events):

            start_time = event["start"]
            end_time = event["end"]

            time = f"{start_time:%H:%M}–{end_time:%H:%M}"

            event_type = event["type"].replace("_", " ").title()
            event_class = event["type"].lower()

            people = ", ".join(event["people"])

            speaker_html = ""

            if people:
                speaker_html = f"""
<div class="course-schedule-speaker">
{people}
</div>
"""

            location_html = ""

            if event["location"]:
                location_html = f"""
<div class="course-schedule-location">
<i class="bi bi-geo-alt"></i>
{event["location"]}
</div>
"""

            # ----------------------------------------------------------
            # Link event title to its content page, if provided
            # ----------------------------------------------------------

            content = event.get("content", "")

            if content:
                content = content.replace(".qmd", ".html")
                title_html = f'<a href="{content}">{event["title"]}</a>'
            else:
                title_html = event["title"]

            separator_html = ""

            if index > 0:
                separator_html = """
<div class="course-schedule-separator"></div>
"""

            rows.append(
                f"""
<div class="course-schedule-event">

{separator_html}

<div class="course-schedule-time">
{time}
</div>

<div class="course-schedule-details">

<span class="course-upcoming-type course-type-{event_class}">
{event_type}
</span>

<h3 class="course-schedule-title">
{title_html}
</h3>

{speaker_html}

</div>

<div class="course-schedule-location-column">

{location_html}

</div>

</div>
"""
            )

        timeline.append(
            f"""
<section
id="{day_id}"
class="course-schedule-day">

<h2 class="course-schedule-day-heading">
{group} – {weekday}, {month} {day}
</h2>

{''.join(rows)}

</section>
"""
        )

    schedule = f"""
<div class="course-schedule">

<div class="course-schedule-sidebar">

{''.join(sidebar)}

</div>

<div class="course-schedule-timeline">

{''.join(timeline)}

</div>

</div>
""".strip()

    return f"""
{page_header}

{schedule}
""".strip()