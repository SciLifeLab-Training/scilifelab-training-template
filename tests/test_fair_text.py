"""Plain text in the citation files, and authorship in the README."""

import scripts.generate_landing  # noqa: F401  (puts scripts/ on the path)
from renderers import fair


def test_markdown_is_removed_from_plain_text() -> None:
    text = (
        "R is a **free** language. See [CRAN](https://cran.r-project.org) "
        "and `library()`.\n\nIt covers:\n\n- data import\n- _plots_\n"
    )

    assert fair._plain_paragraphs(text) == [
        "R is a free language. See CRAN and library().",
        "It covers:",
        "data import; plots.",
    ]


def test_plain_text_keeps_underscores_inside_words() -> None:
    assert fair._plain_text("Use snake_case_names.") == "Use snake_case_names."


def test_readme_contributors_show_who_is_an_author() -> None:
    team = {
        "members": [
            {"name": "Anna Lindqvist", "roles": ["Founder"], "affiliation": "A"},
            {
                "name": "Jonas Ek",
                "roles": ["Contributor"],
                "affiliation": "B",
                "citation_author": False,
            },
        ]
    }

    lines = fair._readme_contributors({}, team, {})
    table = "\n".join(lines)

    assert "| Name | Role | Author | ORCID | Affiliation |" in table
    assert "| Anna Lindqvist | Founder | Yes |" in table
    assert "| Jonas Ek | Contributor | No |" in table
    assert "listed on Zenodo as contributors" in table


def test_non_authors_get_a_zenodo_contributor_type() -> None:
    team = {
        "members": [
            {
                "name": "Jonas Ek",
                "roles": ["Contributor"],
                "affiliation": "B",
                "citation_author": False,
            },
        ]
    }

    contributors = fair._zenodo_contributors(team)

    assert contributors[0]["type"] == "ProjectMember"
