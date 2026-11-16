"""
Check the data files before the website is rendered.

Each check stops the render with a clear message that explains
what is wrong and how to fix it in the data files.
"""

import re
from datetime import date, datetime
from renderers.fair import licence_id, repository_url

DOI_PATTERN = r"^(https?://(dx\.)?doi\.org/|doi:)?10\.\d{4,9}/\S+$"
ORCID_PATTERN = r"^(https://orcid\.org/)?\d{4}-\d{4}-\d{4}-\d{3}[\dX]$"

ALLOWED_ROLES = {
    "Training lead",
    "Instructor",
    "Contributor",
}


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _check_date(value, field):
    """Return a date, or raise an error when it is not YYYY-MM-DD."""

    value = str(value or "").strip()

    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(
            f"{field} is not a valid date: '{value}'. "
            "Write it as YYYY-MM-DD."
        ) from None


# ---------------------------------------------------------
# course.yml
# ---------------------------------------------------------

def validate_course(course):

    required = [
        "title",
        "description",
        "mode",
        "language",
        "location",
        "target_audience",
        "learning_outcomes",
        "keywords",
        "organizers",
        "contact",
    ]

    for field in required:
        if not course.get(field):
            raise ValueError(f"course.{field} is required")

    if not isinstance(course["learning_outcomes"], list):
        raise ValueError("course.learning_outcomes must be a list")

    if not course["learning_outcomes"]:
        raise ValueError(
            "course.learning_outcomes must contain at least one item"
        )

    if not isinstance(course["organizers"], list):
        raise ValueError("course.organizers must be a list")

    if not course["organizers"]:
        raise ValueError(
            "course.organizers must contain at least one item"
        )

    if not isinstance(course["keywords"], list):
        raise ValueError("course.keywords must be a list")
    
    if not isinstance(course["contact"], dict):
        raise ValueError("course.contact must be a mapping")

    if not course["contact"].get("email"):
        raise ValueError("course.contact.email is required")

    # Training dates are optional, for example for self-paced training.
    start = _check_date(course.get("start_date"), "course.start_date")
    end = _check_date(course.get("end_date"), "course.end_date")

    if start and end and end < start:
        raise ValueError("course.end_date is before course.start_date")

    # Reuse, citation and DOI.
    reuse = course.get("reuse") or {}

    for field in ["doi", "version_doi"]:
        value = str(reuse.get(field) or "").strip()

        if value and not re.match(DOI_PATTERN, value, re.IGNORECASE):
            raise ValueError(
                f"course.reuse.{field} is not a valid DOI: '{value}'. "
                'Write it like "10.5281/zenodo.1234567".'
            )

    _check_date(reuse.get("release_date"), "course.reuse.release_date")

    # A licence is needed for the citation, Zenodo and Bioschemas, and must
    # be one fair.py recognises, or be given as an SPDX code in licence_id.
    if not str(reuse.get("licence") or reuse.get("licence_id") or "").strip():
        raise ValueError(
            'course.reuse.licence is required, for example "CC BY 4.0".'
        )

    if not licence_id(course):
        raise ValueError(
            f"course.reuse.licence '{reuse.get('licence')}' is not "
            "recognised. Add its short code from https://spdx.org/licenses/ "
            "to course.reuse.licence_id."
        )

    return course


# ---------------------------------------------------------
# website.yml
# ---------------------------------------------------------

def validate_website(website):

    pages = website.get("pages")

    if pages is not None and not isinstance(pages, dict):
        raise ValueError(
            "website.pages must contain one entry per quick link, "
            "such as content, syllabus and schedule"
        )

    if not isinstance(website.get("template", False), bool):
        raise ValueError(
            "website.template must be true or false"
        )

    if not isinstance(website.get("previous_instance_banner", True), bool):
        raise ValueError(
            "website.previous_instance_banner must be true or false"
        )

    footer = website.get("footer") or {}
    explicit = str((footer.get("repository") or {}).get("url") or "").strip()
    github = r"^https://github\.com/[^/\s]+/[^/\s]+?/?$"

    if explicit and not re.match(github, explicit):
        raise ValueError(
            "website.footer.repository.url must be the GitHub address of "
            "this repository, for example "
            '"https://github.com/organisation/repository". '
            "You can also leave it out: it is then worked out automatically."
        )

    if not re.match(github, repository_url(website)):
        raise ValueError(
            "Could not work out the GitHub address of this repository. "
            "Add it to data/website.yml as footer.repository.url, for "
            'example "https://github.com/organisation/repository".'
        )

    for old_key in ("organisation", "licence"):
        if old_key in footer:
            print(
                f"Note: footer.{old_key} in data/website.yml is no longer "
                "used. The footer now takes it from data/course.yml "
                "(organizers and reuse.licence). You can delete it."
            )

    return website


# ---------------------------------------------------------
# schedule.yml
# ---------------------------------------------------------

EVENT_FIELDS = ["title", "type", "group", "start", "end"]

# A date and time, with or without seconds: 2027-05-12T09:00 or
# 2027-05-12T09:00:00. A space instead of the T is also accepted.
DATETIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?$"
)


def _check_datetime(value, field, title):
    """
    Return a date and time, or raise an error that explains the format.

    Data files read 2027-05-12T09:00:00 as a date and time, but
    2027-05-12T09:00, without seconds, as text. Both are accepted here,
    so the shorter form can be used.
    """

    if isinstance(value, datetime):
        return value.replace(tzinfo=None)

    text = str(value or "").strip()

    if DATETIME_PATTERN.match(text):
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            pass

    raise ValueError(
        f'schedule.yml: the {field} of "{title}" is not a valid date and '
        f"time: '{text}'. Write it as YYYY-MM-DDTHH:MM, with the 24-hour "
        "clock, for example 2027-05-12T09:00."
    )


def validate_schedule(events):

    if not isinstance(events, list):
        raise ValueError("schedule.yml must contain an 'events' list")

    checked = []

    for number, event in enumerate(events, start=1):

        if not isinstance(event, dict):
            raise ValueError(
                f"schedule.yml: event {number} must start with '- title:' "
                "and have its fields indented below it."
            )

        title = str(event.get("title") or f"event {number}").strip()

        missing = [
            field for field in EVENT_FIELDS
            if not str(event.get(field) or "").strip()
        ]

        if missing:
            raise ValueError(
                f'schedule.yml: "{title}" needs '
                + ", ".join(missing)
                + ". Every event needs a title, type, group, start and end."
            )

        start = _check_datetime(event["start"], "start", title)
        end = _check_datetime(event["end"], "end", title)

        if end < start:
            raise ValueError(
                f'schedule.yml: "{title}" ends before it starts. '
                "Check its start and end."
            )

        checked.append({**event, "start": start, "end": end})

    return checked


# ---------------------------------------------------------
# team.yml
# ---------------------------------------------------------

def validate_team(team):

    if not isinstance(team, dict):
        raise ValueError(
            "team.yml must contain a 'team' mapping"
        )

    members = team.get("members")

    if not isinstance(members, list):
        raise ValueError(
            "team.members must be a list"
        )

    if not members:
        raise ValueError(
            "team.members must contain at least one member"
        )

    course_contact_found = False

    required = [
        "name",
        "roles",
        "affiliation",
    ]

    for member in members:

        member_name = member.get(
            "name",
            "<unnamed member>"
        )

        for field in required:

            if not member.get(field):
                if field == "name":
                    raise ValueError(
                        "A team member is missing a name: fill in "
                        "'given_names' and 'family_names'"
                    )

                raise ValueError(
                    f"Team member '{member_name}' "
                    f"is missing '{field}'"
                )

        if not isinstance(member["roles"], list):
            raise ValueError(
                f"Team member '{member_name}' "
                "roles must be a list"
            )

        if not member["roles"]:
            raise ValueError(
                f"Team member '{member_name}' "
                "must have at least one role"
            )

        invalid_roles = set(member["roles"]) - ALLOWED_ROLES

        if invalid_roles:
            invalid = ", ".join(sorted(invalid_roles))

            raise ValueError(
                f"Team member '{member_name}' "
                f"has invalid role(s): {invalid}. "
                "Allowed roles are: Training lead, "
                "Instructor, Contributor"
            )

        orcid = str(member.get("orcid") or "").strip()

        if orcid and not re.match(ORCID_PATTERN, orcid):
            raise ValueError(
                f"Team member '{member_name}' has an invalid ORCID: "
                f"'{orcid}'. Write it like "
                '"https://orcid.org/0000-0002-1825-0097".'
            )

        if member.get("course_contact") is True:

            if not member.get("email"):
                raise ValueError(
                    f"Team member '{member_name}' "
                    "is marked as course_contact but "
                    "has no email address"
                )

            course_contact_found = True

    # CITATION.cff and Zenodo need at least one author.
    if all(member.get("citation_author") is False for member in members):
        raise ValueError(
            "At least one team member must be a citation author: remove "
            "'citation_author: false' from at least one member."
        )

    if not course_contact_found:
        raise ValueError(
            "At least one team member must have "
            "'course_contact: true' and an email address"
        )

    return team
