"""
Check the data files before the website is rendered.

Each check stops the render with a clear message that explains
what is wrong and how to fix it in the data files.
"""

import re
from datetime import date


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

    return course


# ---------------------------------------------------------
# website.yml
# ---------------------------------------------------------

def validate_website(website):

    pages = website.get("pages", {})

    required_pages = [
        "content",
        "syllabus",
    ]

    for page in required_pages:

        if page not in pages:
            raise ValueError(
                f"Required page '{page}' is missing"
            )

    footer = website.get("footer") or {}
    repository = str((footer.get("repository") or {}).get("url") or "").strip()

    if not re.match(r"^https://github\.com/[^/\s]+/[^/\s]+?/?$", repository):
        raise ValueError(
            "website.footer.repository.url must be the GitHub address of "
            "this repository, for example "
            '"https://github.com/organisation/repository"'
        )
    
    return website


# ---------------------------------------------------------
# schedule.yml
# ---------------------------------------------------------

def validate_schedule(events):

    if not isinstance(events, list):
        raise ValueError("schedule.yml must contain an 'events' list")

    return events


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

    if not course_contact_found:
        raise ValueError(
            "At least one team member must have "
            "'course_contact: true' and an email address"
        )

    return team
