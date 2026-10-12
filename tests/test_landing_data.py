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
