#!/usr/bin/env python3

from pathlib import Path
import shutil

from loaders import (
    load_course,
    load_website,
    load_content,
    load_schedule,
    load_team,
    load_announcements,
    load_practicalities,
    load_faq,
    load_preparation,
    load_resources
)

from content import load_content_sections

from validators import (
    validate_course,
    validate_website,
    validate_schedule,
    validate_team,
)

from writer import write_partial

from renderers.welcome import render_welcome
from renderers.navbar import (
    render_navbar_meta,
    render_navbar_brand,
    render_navbar_links,
)
from renderers.registration import render_registration
from renderers.upcoming import render_upcoming
from renderers.quick_links import render_quick_links
from renderers.announcements import (
    render_announcements,
    render_announcements_page,
)
from renderers.team import render_team
from renderers.team_page import render_team_page
from renderers.content import (
    render_content_navbar,
    render_content_navigation,
    render_content_next_navigation,
    render_content_footer,
)
from renderers.schedule import render_schedule
from renderers.syllabus import render_syllabus
from renderers.practicalities import render_practicalities
from renderers.faq import render_faq
from renderers.preparation import render_preparation
from renderers.footer import render_footer
from renderers.resources import render_resources
from renderers.fair import write_fair_files, render_bioschemas


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "_generated"

def complete_names(team):
    """
    Build each team member's display name from given_names and
    family_names, when no name is given.
    """

    for member in team.get("members") or []:
        if str(member.get("name") or "").strip():
            continue

        parts = [
            str(member.get("given_names") or "").strip(),
            str(member.get("family_names") or "").strip(),
        ]

        member["name"] = " ".join(part for part in parts if part)

    return team


def main():
    print("Running course renderer...")

    # Start every render with a clean generated directory.
    if GENERATED_DIR.exists():
        shutil.rmtree(GENERATED_DIR)

    GENERATED_DIR.mkdir()

    course = validate_course(load_course())
    website = validate_website(load_website())
    content = load_content()
    sections = load_content_sections(content)
    registration = website.get("registration", {})
    events = validate_schedule(load_schedule())
    team = validate_team(complete_names(load_team()))
    announcements = load_announcements()
    practicalities = load_practicalities()
    faq = load_faq()
    preparation = load_preparation()
    resources = load_resources()

    available_pages = set()

    if events:
        available_pages.add("schedule")

    if practicalities:
        available_pages.add("practicalities")

    if faq:
        available_pages.add("faq")

    if preparation.get("sections"):
        available_pages.add("preparation")

    if resources:
        available_pages.add("resources")

    if announcements.get("items"):
        available_pages.add("announcements")

    write_partial(
        "welcome.qmd",
        render_welcome(course, website),
    )

    write_partial(
        "navbar_meta.qmd",
        render_navbar_meta(course),
    )

    write_partial(
        "navbar_brand.qmd",
        render_navbar_brand(website),
    )

    write_partial(
        "navbar_links.qmd",
        render_navbar_links(website, available_pages),
    )

    write_partial(
        "registration.qmd",
        render_registration(registration),
    )

    write_partial(
        "upcoming.qmd",
        render_upcoming(events),
    )

    write_partial(
        "quick_links.qmd",
        render_quick_links(website, events),
    )

    write_partial(
        "announcements.qmd",
        render_announcements(announcements),
    )

    write_partial(
        "announcements_page.qmd",
        render_announcements_page(announcements),
    )

    write_partial(
        "team.qmd",
        render_team(team),
    )

    write_partial(
        "team_page.qmd",
        render_team_page(team),
    )

    write_partial(
        "schedule.qmd",
        render_schedule(events, course),
    )

    content_navigation = render_content_navigation(sections)

    write_partial(
        "content-navbar.html",
        render_content_navbar(
            course,
            website,
            available_pages,
            content_navigation,
        ),
    )

    write_partial(
    "content-next-navigation.html",
    render_content_next_navigation(sections),
    )   
    
    write_partial(
        "syllabus.qmd",
        render_syllabus(course, team, website),
    )

    write_partial(
        "practicalities.qmd",
        render_practicalities(practicalities, course),
    )

    write_partial(
        "faq.qmd",
        render_faq(faq),
    )

    write_partial(
        "preparation.qmd",
        render_preparation(preparation, course),
    )

    write_partial(
        "footer.qmd",
        render_footer(website),
    )

    write_partial(
        "content-footer.html",
        render_content_footer(website),
    )

    write_partial(
        "resources.qmd",
        render_resources(resources),
    )

    write_partial(
        "bioschemas.html",
        render_bioschemas(course, team, website),
    )

    write_fair_files(ROOT, course, team, website)

if __name__ == "__main__":
    main()