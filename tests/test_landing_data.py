"""Tests for the data-driven landing page and its FAIR metadata."""

from __future__ import annotations

import copy
import json

import pytest

import scripts.generate_landing as gl
from renderers import fair, landing


@pytest.fixture
def landing_data():
    """The landing data files of the repository, loaded and checked."""

    return gl.load_landing_data()


def test_repository_data_files_are_valid(landing_data) -> None:
    course, team, website = landing_data
    assert course["title"]
    assert team["members"]
    assert website["labels"]["instances_band_title"]


def test_template_metadata_is_valid() -> None:
    course, team, website = gl.load_landing_data()
    website["template"] = True
    template_course, template_team = gl.load_citation_data(course, team, website)
    assert template_course["title"] != course["title"]
    assert template_team["members"]


def test_course_requires_keywords(landing_data) -> None:
    course = copy.deepcopy(landing_data[0])
    course["keywords"] = []
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_course(course)
    assert "course.keywords" in str(exc.value)


def test_course_rejects_invalid_doi(landing_data) -> None:
    course = copy.deepcopy(landing_data[0])
    course["reuse"]["doi"] = "DOI, if applicable"
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_course(course)
    assert "not a valid DOI" in str(exc.value)


def test_team_only_allows_founders_and_contributors(landing_data) -> None:
    team = copy.deepcopy(landing_data[1])
    team["members"][0]["roles"] = ["Instructor"]
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_team(team)
    assert "Allowed roles are: Founder, Contributor" in str(exc.value)


def test_team_requires_names() -> None:
    team = {"members": [{"roles": ["Founder"], "affiliation": "X"}]}
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_team(gl.complete_names(team))
    assert "missing a name" in str(exc.value)


def test_website_requires_github_repository(landing_data) -> None:
    website = copy.deepcopy(landing_data[2])
    website["footer"]["repository"]["url"] = "https://example.org/repo"
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_website(website)
    assert "GitHub address" in str(exc.value)


def test_template_banner_only_in_template_mode(landing_data) -> None:
    website = copy.deepcopy(landing_data[2])
    website["template"] = True
    assert "template-banner" in landing.render_template_banner(website)
    website["template"] = False
    assert landing.render_template_banner(website) == ""


def test_empty_topics_card_is_left_out(landing_data) -> None:
    course = copy.deepcopy(landing_data[0])
    assert "Topics covered" in landing.render_top_cards(course)
    course["topics"] = []
    assert "Topics covered" not in landing.render_top_cards(course)


def test_bottom_cards_list_founders_and_contributors(landing_data) -> None:
    team = landing_data[1]
    cards = landing.render_bottom_cards(team)
    founders = [m["name"] for m in team["members"] if "Founder" in m["roles"]]
    assert "Founders" in cards
    assert all(name in cards for name in founders)


def test_course_bioschemas_has_course_only(landing_data) -> None:
    course, team, website = landing_data
    markup = fair.render_bioschemas(course, team, website, scope="course")
    data = json.loads(markup.split("\n", 1)[1].rsplit("\n", 1)[0])
    assert data["@type"] == "Course"
    assert "hasCourseInstance" not in data
    # The same @id as on the instance pages: the landing page + #course.
    assert data["@id"] == fair.pages_url(website) + "#course"


def test_course_citation_has_no_instance_version(landing_data) -> None:
    course, team, website = landing_data
    cff = fair.render_citation_cff(course, team, website, scope="course")
    assert "\nversion:" not in cff
    assert f"url: {fair.pages_url(website)}" in cff


def test_scope_is_reset_after_a_call(landing_data) -> None:
    course, team, website = landing_data
    fair.render_citation_cff(course, team, website, scope="course")
    assert fair._SCOPE == "instance"


def test_template_citation_is_software() -> None:
    course, team, website = gl.load_landing_data()
    website["template"] = True
    template_course, template_team = gl.load_citation_data(course, team, website)
    zenodo = json.loads(
        fair.render_zenodo_json(template_course, template_team, website, scope="course")
    )
    assert zenodo["upload_type"] == "software"
    assert zenodo["version"]

def test_course_requires_a_licence(landing_data) -> None:
    course = copy.deepcopy(landing_data[0])
    course["reuse"]["licence"] = ""
    course["reuse"]["licence_id"] = ""
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_course(course)
    assert "licence is required" in str(exc.value)


def test_course_rejects_unknown_licence_without_id(landing_data) -> None:
    course = copy.deepcopy(landing_data[0])
    course["reuse"]["licence"] = "My own licence"
    course["reuse"]["licence_id"] = ""
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_course(course)
    assert "not recognised" in str(exc.value)

    course["reuse"]["licence_id"] = "LicenseRef-own"
    gl.validate_course(course)


def test_team_needs_a_citation_author(landing_data) -> None:
    team = copy.deepcopy(landing_data[1])
    for member in team["members"]:
        member["citation_author"] = False
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_team(team)
    assert "citation author" in str(exc.value)

def test_logo_height_is_used_and_defaults_to_56(landing_data) -> None:
    website = copy.deepcopy(landing_data[2])
    website["hero"]["logos"] = [
        {"src": "img/logos/a.svg", "alt": "A", "height": 40},
        {"src": "img/logos/b.svg", "alt": "B"},
    ]
    brand = landing.render_hero_brand(website)
    assert "--logo-height: 40px;" in brand
    assert "--logo-height: 56px;" in brand


@pytest.mark.parametrize("height", [0, -10, "big", True])
def test_logo_height_must_be_a_positive_number(landing_data, height) -> None:
    website = copy.deepcopy(landing_data[2])
    website["hero"]["logos"][0]["height"] = height
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_website(website)
    assert "positive number of pixels" in str(exc.value)


def test_primary_logo_is_shown_last(landing_data) -> None:
    website = copy.deepcopy(landing_data[2])
    website["hero"]["logos"] = [
        {"src": "img/logos/main.svg", "alt": "Main", "primary": True},
        {"src": "img/logos/a.svg", "alt": "A"},
        {"src": "img/logos/b.svg", "alt": "B"},
    ]
    brand = landing.render_hero_brand(website)
    assert brand.index("a.svg") < brand.index("b.svg") < brand.index("main.svg")


def test_only_one_primary_logo(landing_data) -> None:
    website = copy.deepcopy(landing_data[2])
    website["hero"]["logos"] = [
        {"src": "img/logos/a.svg", "alt": "A", "primary": True},
        {"src": "img/logos/b.svg", "alt": "B", "primary": True},
    ]
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_website(website)
    assert "Only one logo" in str(exc.value)


def test_footer_takes_organisation_and_licence_from_course(landing_data) -> None:
    from renderers.footer import render_footer

    course = copy.deepcopy(landing_data[0])
    course["organizers"] = ["Org A", "Org B", "Org C"]
    course["reuse"]["licence"] = "CC BY-SA 4.0"
    course["reuse"]["licence_url"] = ""
    footer = render_footer(landing_data[2], course)
    assert "By Org A, Org B and Org C." in footer
    assert (
        'Licensed under <a href="https://spdx.org/licenses/CC-BY-SA-4.0.html">'
        "CC BY-SA 4.0</a>." in footer
    )


def test_repository_url_is_detected_on_github(landing_data, monkeypatch) -> None:
    website = copy.deepcopy(landing_data[2])
    website["footer"]["repository"].pop("url", None)
    monkeypatch.setenv("GITHUB_REPOSITORY", "my-org/my-training")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    assert fair.repository_url(website) == "https://github.com/my-org/my-training"


@pytest.mark.parametrize(
    "remote",
    [
        "https://github.com/my-org/my-training.git",
        "git@github.com:my-org/my-training.git",
        "ssh://git@github.com/my-org/my-training",
    ],
)
def test_github_remote_addresses_are_recognised(remote) -> None:
    match = fair.GITHUB_REMOTE_PATTERN.match(remote)
    assert match and match.groups() == ("my-org", "my-training")


def test_explicit_repository_url_wins(landing_data, monkeypatch) -> None:
    website = copy.deepcopy(landing_data[2])
    website["footer"]["repository"]["url"] = "https://github.com/other/repo"
    monkeypatch.setenv("GITHUB_REPOSITORY", "my-org/my-training")
    assert fair.repository_url(website) == "https://github.com/other/repo"


def test_missing_repository_url_is_reported(landing_data, monkeypatch) -> None:
    website = copy.deepcopy(landing_data[2])
    website["footer"]["repository"].pop("url", None)
    monkeypatch.setattr(fair, "detected_repository_url", lambda: "")
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_website(website)
    assert "Could not work out" in str(exc.value)
