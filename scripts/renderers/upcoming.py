import json


MONTHS = [
    "JAN", "FEB", "MAR", "APR",
    "MAY", "JUN", "JUL", "AUG",
    "SEP", "OCT", "NOV", "DEC",
]


def render_upcoming(events):

    if not events:
        return ""

    # ------------------------------------------------------------------
    # Prepare event data for JavaScript
    # ------------------------------------------------------------------

    event_data = []

    for event in events:

        start = event["start"]
        end = event["end"]

        content = event.get("content", "")

        if content:
            content = content.replace(".qmd", ".html")

        event_data.append({
            "title": event["title"],
            "type": event["type"],
            "group": event["group"],
            "start": start.isoformat(),
            "end": end.isoformat(),
            "location": event.get("location", ""),
            "people": event.get("people", []),
            "content": content,
        })

    events_json = json.dumps(event_data)

    # ------------------------------------------------------------------
    # Render complete Upcoming section
    # ------------------------------------------------------------------

    return f"""
::: {{.course-upcoming-section}}

<div class="course-section-label">

NEXT UP

</div>

<div
    class="course-upcoming"
    data-events='{events_json}'>

<div class="course-upcoming-card">

<div class="course-upcoming-day">
<div class="course-upcoming-weekday"></div>
<div class="course-upcoming-date"></div>
<div class="course-upcoming-month"></div>
</div>

<div class="course-upcoming-details">

<div class="course-upcoming-top">
<span class="course-upcoming-time"></span>
<span class="course-upcoming-type"></span>
</div>

<h3 class="course-upcoming-title"></h3>

<div class="course-upcoming-speaker"></div>

<div class="course-upcoming-location"></div>

</div>

<div class="course-upcoming-status">

<div class="course-upcoming-countdown"></div>

<a
    class="course-upcoming-link course-text-link"
    href="schedule.qmd">
    Full schedule →
</a>

</div>

</div>

</div>

:::
""".strip()