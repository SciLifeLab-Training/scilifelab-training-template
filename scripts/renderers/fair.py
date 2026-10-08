"""
Generate FAIR metadata for a training instance.

All metadata is generated from the existing data files
(course.yml, team.yml and website.yml), so there is only one
place to edit:

- CITATION.cff       citation metadata (GitHub, reference managers)
- .zenodo.json       metadata for the Zenodo record of each release
- README.md          the "About this training" section between the markers
- bioschemas.html    Bioschemas JSON-LD for the overview page (e.g. for TeSS)

The generated files should never be edited by hand: they are
overwritten on every render.
"""

import json
import os
import re
import subprocess
from datetime import date, datetime
from pathlib import Path

import yaml


# ---------------------------------------------------------
# Constants
# ---------------------------------------------------------

CFF_MESSAGE = (
    "If you use or reuse these training materials, "
    "please cite them as below."
)

GENERATED_NOTICE = (
    "This file is generated automatically from the data files "
    "in data/. Do not edit it by hand: edit the data files instead."
)

README_START = "<!-- training-info:start -->"
README_END = "<!-- training-info:end -->"

BIOSCHEMAS_COURSE = "https://bioschemas.org/profiles/Course/1.0-RELEASE"
BIOSCHEMAS_COURSE_INSTANCE = (
    "https://bioschemas.org/profiles/CourseInstance/1.0-RELEASE"
)
DCT_CONFORMS_TO = "http://purl.org/dc/terms/conformsTo"

# Licence names as written in course.yml, mapped to SPDX identifiers.
# Keys are normalised: upper case, without spaces, hyphens or underscores.
SPDX_LICENCES = {
    "CCBY4.0": "CC-BY-4.0",
    "CCBYSA4.0": "CC-BY-SA-4.0",
    "CCBYNC4.0": "CC-BY-NC-4.0",
    "CCBYNCSA4.0": "CC-BY-NC-SA-4.0",
    "CCBYND4.0": "CC-BY-ND-4.0",
    "CCBYNCND4.0": "CC-BY-NC-ND-4.0",
    "CC01.0": "CC0-1.0",
    "CC0": "CC0-1.0",
    "MIT": "MIT",
    "APACHE2.0": "Apache-2.0",
    "BSD3CLAUSE": "BSD-3-Clause",
    "GPL3.0": "GPL-3.0-only",
}

# Common language names, mapped to a BCP 47 tag (used by Bioschemas)
# and an ISO 639-3 code (used by Zenodo).
LANGUAGES = {
    "english": ("en", "eng"),
    "swedish": ("sv", "swe"),
    "svenska": ("sv", "swe"),
    "norwegian": ("no", "nor"),
    "danish": ("da", "dan"),
    "finnish": ("fi", "fin"),
    "german": ("de", "deu"),
    "french": ("fr", "fra"),
    "spanish": ("es", "spa"),
}

# Order in which team members are listed as authors.
ROLE_ORDER = ["Training lead", "Instructor", "Contributor"]

DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$")
ORCID_PATTERN = re.compile(
    r"^https://orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[\dX]$"
)
INSTANCE_BRANCH_PATTERN = re.compile(r"^release-(\d{4})$")


# ---------------------------------------------------------
# Small helpers
# ---------------------------------------------------------

def _text(value):
    """Return a value as a single-line string, or "" when empty."""

    if value is None:
        return ""

    return " ".join(str(value).split())


def _date(value):
    """Return a date as YYYY-MM-DD, or "" when it is not a valid date."""

    if isinstance(value, datetime):
        return value.date().isoformat()

    if isinstance(value, date):
        return value.isoformat()

    value = _text(value)

    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        return ""


def _list(values):
    """Return a list of non-empty single-line strings."""

    return [
        _text(value)
        for value in (values or [])
        if _text(value)
    ]


def _clean_doi(value):
    """Return a bare DOI, or "" when the value is not a real DOI."""

    doi = re.sub(
        r"^(https?://(dx\.)?doi\.org/|doi:)",
        "",
        _text(value),
        flags=re.I,
    )

    return doi if DOI_PATTERN.match(doi) else ""


def concept_doi(course):
    """
    Return the concept DOI of the training.

    The concept DOI (reuse.doi) stands for the training as a whole
    and always resolves to its latest version on Zenodo.
    """

    return _clean_doi((course.get("reuse") or {}).get("doi"))


def version_doi(course):
    """
    Return the version DOI of this training instance.

    Zenodo assigns it when the release is published, so it can only
    be added to reuse.version_doi afterwards.
    """

    return _clean_doi((course.get("reuse") or {}).get("version_doi"))


def _doi(course):
    """Return the most specific DOI: the version DOI, or the concept DOI."""

    return version_doi(course) or concept_doi(course)


def _language(course):
    """Return the language as (BCP 47 tag, ISO 639-3 code)."""

    language = _text(course.get("language"))

    return LANGUAGES.get(language.lower(), (language, ""))


def _orcid(value):
    """Return a full ORCID URL, or "" when it is not a valid ORCID."""

    value = _text(value)

    if re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", value):
        value = f"https://orcid.org/{value}"

    return value if ORCID_PATTERN.match(value) else ""


def licence_id(course):
    """
    Return the SPDX identifier of the licence.

    Uses reuse.licence_id when given, otherwise recognises
    common licence names such as "CC BY 4.0".
    """

    reuse = course.get("reuse") or {}

    explicit = _text(reuse.get("licence_id"))

    if explicit:
        return explicit

    name = re.sub(r"[\s\-_]", "", _text(reuse.get("licence")).upper())

    return SPDX_LICENCES.get(name, "")


def licence_url(course):
    """Return the licence URL from course.yml, or the SPDX page."""

    reuse = course.get("reuse") or {}
    url = _text(reuse.get("licence_url"))

    if url:
        return url

    spdx = licence_id(course)

    return f"https://spdx.org/licenses/{spdx}.html" if spdx else ""


# ---------------------------------------------------------
# Instance, repository and website
# ---------------------------------------------------------

def instance_id():
    """
    Return the instance id (YYMM) from the release-YYMM branch name.

    Uses the GitHub Actions branch name when available, and
    the local Git branch otherwise.
    """

    branch = os.environ.get("GITHUB_REF_NAME", "")

    if not branch:
        try:
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            branch = ""

    match = INSTANCE_BRANCH_PATTERN.match(branch)

    return match.group(1) if match else ""


def repository_url(website):
    """Return the repository URL from website.yml."""

    footer = website.get("footer") or {}
    repository = footer.get("repository") or {}

    return _text(repository.get("url"))


def website_url(course, website):
    """
    Return the URL of this training instance's website.

    Uses reuse.website_url when given. Otherwise it is derived
    from the GitHub repository URL and the instance id, e.g.
    https://organisation.github.io/repository/2505/
    """

    reuse = course.get("reuse") or {}
    explicit = _text(reuse.get("website_url"))

    if explicit:
        return explicit

    match = re.match(
        r"^https://github\.com/([^/]+)/([^/]+?)(\.git)?/?$",
        repository_url(website),
    )

    instance = instance_id()

    if not match or not instance:
        return ""

    owner, repo = match.group(1).lower(), match.group(2)

    return f"https://{owner}.github.io/{repo}/{instance}/"


def course_url(course, website):
    """
    Return the URL of the training as a whole: the landing page
    that lists all instances, e.g.
    https://organisation.github.io/repository/
    """

    instance_url = website_url(course, website)
    instance = instance_id()

    if instance_url and instance:
        return re.sub(rf"{instance}/?$", "", instance_url)

    return instance_url


def version(course):
    """Return the version: reuse.version, or the instance id."""

    reuse = course.get("reuse") or {}

    return _text(reuse.get("version")) or instance_id()


# ---------------------------------------------------------
# People
# ---------------------------------------------------------

def _split_name(member):
    """
    Return (given names, family names) for a team member.

    Uses given_names and family_names from team.yml when given.
    Otherwise the last word of the name is used as the family name.
    """

    given = _text(member.get("given_names"))
    family = _text(member.get("family_names"))

    if given or family:
        return given, family

    words = _text(member.get("name")).split()

    if not words:
        return "", ""

    if len(words) == 1:
        return "", words[0]

    return " ".join(words[:-1]), words[-1]


def authors(team):
    """
    Return the team members to credit as authors.

    Training leads come first, then instructors, then contributors.
    Members with citation_author: false in team.yml are left out.
    """

    members = [
        member
        for member in (team.get("members") or [])
        if _text(member.get("name"))
        and member.get("citation_author", True) is not False
    ]

    def role_rank(member):
        roles = member.get("roles") or []

        ranks = [
            ROLE_ORDER.index(role)
            for role in roles
            if role in ROLE_ORDER
        ]

        return min(ranks) if ranks else len(ROLE_ORDER)

    seen = set()
    ordered = []

    for member in sorted(members, key=role_rank):
        name = _text(member.get("name"))

        if name in seen:
            continue

        seen.add(name)
        ordered.append(member)

    return ordered


def _cff_person(member, include_email=False):
    """Return a team member as a CITATION.cff person."""

    given, family = _split_name(member)

    person = {}

    if family:
        person["family-names"] = family

    if given:
        person["given-names"] = given

    affiliation = _text(member.get("affiliation"))

    if affiliation:
        person["affiliation"] = affiliation

    orcid = _orcid(member.get("orcid"))

    if orcid:
        person["orcid"] = orcid

    email = _text(member.get("email"))

    if include_email and email:
        person["email"] = email

    return person


def _schema_person(member):
    """Return a team member as a schema.org Person."""

    person = {
        "@type": "Person",
        "name": _text(member.get("name")),
    }

    orcid = _orcid(member.get("orcid"))

    if orcid:
        person["@id"] = orcid
        person["identifier"] = orcid

    affiliation = _text(member.get("affiliation"))

    if affiliation:
        person["affiliation"] = {
            "@type": "Organization",
            "name": affiliation,
        }

    return person


def _citation_text(course, team, website):
    """
    Return the citation text shown in the README.

    Uses reuse.preferred_citation when given, otherwise builds
    one from the authors, year, title, version and DOI or URL.
    """

    reuse = course.get("reuse") or {}
    preferred = _text(reuse.get("preferred_citation"))

    if preferred:
        return preferred

    names = []

    for member in authors(team):
        given, family = _split_name(member)
        initials = " ".join(f"{part[0]}." for part in given.split())
        names.append(f"{family}, {initials}".strip(", "))

    year = _date(reuse.get("release_date"))[:4]
    doi = _doi(course)
    link = f"https://doi.org/{doi}" if doi else website_url(course, website)

    parts = [
        "; ".join(names),
        f"({year})." if year else "",
        f"{_text(course.get('title'))}.",
        f"Version {version(course)}." if version(course) else "",
        link,
    ]

    return " ".join(part for part in parts if part)


# ---------------------------------------------------------
# CITATION.cff
# ---------------------------------------------------------

def render_citation_cff(course, team, website):
    """Return the contents of CITATION.cff."""

    cff = {
        "cff-version": "1.2.0",
        "message": CFF_MESSAGE,
        "title": _text(course.get("title")),
    }

    abstract = _text(course.get("description"))

    if abstract:
        cff["abstract"] = abstract

    cff["authors"] = [
        _cff_person(member)
        for member in authors(team)
    ]

    contacts = [
        _cff_person(member, include_email=True)
        for member in team.get("members") or []
        if member.get("course_contact") and _text(member.get("email"))
    ]

    if contacts:
        cff["contact"] = contacts

    keywords = _list(course.get("keywords"))

    if keywords:
        cff["keywords"] = keywords

    spdx = licence_id(course)

    if spdx:
        cff["license"] = spdx

    url = website_url(course, website)

    if url:
        cff["url"] = url

    repository = repository_url(website)

    if repository:
        cff["repository-code"] = repository

    instance_version = version(course)

    if instance_version:
        cff["version"] = instance_version

    released = _date((course.get("reuse") or {}).get("release_date"))

    if released:
        cff["date-released"] = released

    doi = _doi(course)

    if doi:
        cff["doi"] = doi

    if version_doi(course) and concept_doi(course):
        cff["identifiers"] = [
            {
                "type": "doi",
                "value": version_doi(course),
                "description": "This training instance",
            },
            {
                "type": "doi",
                "value": concept_doi(course),
                "description": "All instances of this training (latest version)",
            },
        ]

    header = "".join(
        f"# {line}\n"
        for line in [
            GENERATED_NOTICE,
            "Validate with: cffconvert --validate",
        ]
    )

    return header + yaml.safe_dump(
        cff,
        sort_keys=False,
        allow_unicode=True,
        width=1000,
    )


# ---------------------------------------------------------
# Shared text helpers
# ---------------------------------------------------------

def _dates(course):
    """Return the training dates as text."""

    start = _date(course.get("start_date"))
    end = _date(course.get("end_date"))

    if start and end and start != end:
        return f"{start} – {end}"

    return start or end


# ---------------------------------------------------------
# README.md
# ---------------------------------------------------------

def render_readme_section(course, team, website):
    """Return the generated "About this training" README section."""

    reuse = course.get("reuse") or {}
    url = website_url(course, website)
    doi = _doi(course)

    facts = [
        ("Dates", _dates(course)),
        ("Mode", _text(course.get("mode"))),
        ("Location", _text(course.get("location"))),
        ("Language", _text(course.get("language"))),
        ("Expertise level", _text(course.get("expertise_level"))),
        ("Website", f"<{url}>" if url else ""),
        ("DOI", f"[{doi}](https://doi.org/{doi})" if doi else ""),
    ]

    lines = [
        README_START,
        "<!-- This section is generated automatically from the data files "
        "in data/. Edit the data files instead; text outside the markers "
        "is kept. -->",
        "",
        f"# {_text(course.get('title'))}",
        "",
    ]

    if _text(course.get("subtitle")):
        lines += [f"*{_text(course.get('subtitle'))}*", ""]

    if _text(course.get("description")):
        lines += [_text(course.get("description")), ""]

    lines += [
        f"- **{label}:** {value}"
        for label, value in facts
        if value
    ]

    licence_name = _text(reuse.get("licence")) or licence_id(course)
    link = licence_url(course)

    lines += [
        "",
        "## How to cite",
        "",
        _citation_text(course, team, website),
        "",
        "Citation metadata is available in [CITATION.cff](CITATION.cff).",
        "",
        "## Licence",
        "",
        (
            f"The training materials are licensed under "
            f"[{licence_name}]({link})."
            if licence_name and link
            else "See [LICENSE](LICENSE)."
        ),
        "",
        README_END,
    ]

    return "\n".join(lines)


def update_readme(text, section):
    """
    Replace the generated section of a README.

    Only the text between the start and end markers is replaced.
    When the markers are missing, the section is added at the top.
    """

    pattern = re.compile(
        re.escape(README_START) + r".*?" + re.escape(README_END),
        flags=re.S,
    )

    if pattern.search(text):
        return pattern.sub(lambda _: section, text, count=1)

    return section + "\n\n" + text


# ---------------------------------------------------------
# .zenodo.json
# ---------------------------------------------------------

def _zenodo_creator(member):
    """Return a team member as a Zenodo creator."""

    given, family = _split_name(member)

    creator = {
        "name": ", ".join(part for part in [family, given] if part),
    }

    affiliation = _text(member.get("affiliation"))

    if affiliation:
        creator["affiliation"] = affiliation

    orcid = _orcid(member.get("orcid"))

    if orcid:
        creator["orcid"] = orcid.removeprefix("https://orcid.org/")

    return creator


def render_zenodo_json(course, team, website):
    """
    Return the contents of .zenodo.json.

    Zenodo's GitHub integration reads this file when a release is
    published, and uses it for the new version of the Zenodo record.
    It takes precedence over CITATION.cff.
    """

    reuse = course.get("reuse") or {}
    url = website_url(course, website)

    description = [
        f"<p>{_text(course.get('description'))}</p>"
        if _text(course.get("description")) else "",
        f"<p>Training dates: {_dates(course)}.</p>"
        if _dates(course) else "",
        f'<p>Training website: <a href="{url}">{url}</a></p>'
        if url else "",
    ]

    data = {
        "title": _text(course.get("title")),
        "upload_type": "lesson",
        "description": "\n".join(part for part in description if part),
        "creators": [_zenodo_creator(member) for member in authors(team)],
        "keywords": _list(course.get("keywords")),
        "license": licence_id(course).lower(),
        "access_right": "open",
        "version": version(course),
        "language": _language(course)[1],
        "related_identifiers": (
            [
                {
                    "identifier": url,
                    "relation": "isSupplementedBy",
                    "resource_type": "other",
                }
            ]
            if url else []
        ),
        "communities": [
            {"identifier": community}
            for community in _list(reuse.get("zenodo_communities"))
        ],
    }

    return json.dumps(
        _without_empty(data),
        indent=2,
        ensure_ascii=False,
    ) + "\n"


# ---------------------------------------------------------
# Bioschemas JSON-LD
# ---------------------------------------------------------

def render_bioschemas(course, team, website):
    """
    Return Bioschemas Course and CourseInstance markup as a
    <script type="application/ld+json"> block.
    """

    # The instance has its own page; the course is shared by all instances.
    instance_url = website_url(course, website) or repository_url(website)
    course_page = course_url(course, website) or instance_url

    doi = concept_doi(course)

    # Use the concept DOI as the course identifier when there is one, so
    # all instances are recognised as runs of the same course.
    course_id = f"https://doi.org/{doi}" if doi else f"{course_page}#course"

    members = authors(team)
    prerequisites = course.get("prerequisites") or {}

    organizers = [
        {"@type": "Organization", "name": name}
        for name in _list(course.get("organizers"))
    ]

    instructors = [
        _schema_person(member)
        for member in team.get("members") or []
        if {"Training lead", "Instructor"} & set(member.get("roles") or [])
    ]

    language = _language(course)[0]

    instance = {
        "@type": "CourseInstance",
        "@id": f"{instance_url}#course-instance",
        DCT_CONFORMS_TO: {"@id": BIOSCHEMAS_COURSE_INSTANCE},
        "courseMode": _text(course.get("mode")),
        "location": _text(course.get("location")),
        "startDate": _date(course.get("start_date")),
        "endDate": _date(course.get("end_date")),
        "inLanguage": language,
        "identifier": (
            f"https://doi.org/{version_doi(course)}"
            if version_doi(course) else ""
        ),
        "instructor": instructors,
        "organizer": organizers,
        "url": instance_url,
    }

    data = {
        "@context": "https://schema.org/",
        "@type": "Course",
        "@id": course_id,
        DCT_CONFORMS_TO: {"@id": BIOSCHEMAS_COURSE},
        "name": _text(course.get("title")),
        "description": _text(course.get("description")),
        "keywords": ", ".join(_list(course.get("keywords"))),
        "url": course_page,
        "identifier": f"https://doi.org/{doi}" if doi else "",
        "license": licence_url(course),
        "educationalLevel": _text(course.get("expertise_level")),
        "teaches": _list(course.get("learning_outcomes")),
        "coursePrerequisites": (
            _list(prerequisites.get("knowledge"))
            + _list(prerequisites.get("technical"))
        ),
        "audience": (
            {
                "@type": "Audience",
                "audienceType": _text(course.get("target_audience")),
            }
            if _text(course.get("target_audience"))
            else ""
        ),
        "provider": organizers,
        "creator": [_schema_person(member) for member in members],
        "hasCourseInstance": [_without_empty(instance)],
    }

    data = _without_empty(data)

    # Escape "</" so the JSON cannot close the script element early.
    json_ld = json.dumps(data, indent=2, ensure_ascii=False).replace(
        "</", "<\\/"
    )

    return (
        '<script type="application/ld+json">\n'
        f"{json_ld}\n"
        "</script>"
    )


def _without_empty(data):
    """Remove empty strings, lists and dictionaries."""

    return {
        key: value
        for key, value in data.items()
        if value not in ("", [], {}, None)
    }


# ---------------------------------------------------------
# Writing the files
# ---------------------------------------------------------

def _write_if_changed(path, content):
    """Write a file only when its content changes."""

    path = Path(path)

    if path.exists() and path.read_text(encoding="utf-8") == content:
        return

    path.write_text(content, encoding="utf-8")
    print(f"Updated {path.name}")


def write_fair_files(root, course, team, website):
    """
    Write CITATION.cff, .zenodo.json and the generated
    README section to the repository root.
    """

    root = Path(root)

    _write_if_changed(
        root / "CITATION.cff",
        render_citation_cff(course, team, website),
    )

    _write_if_changed(
        root / ".zenodo.json",
        render_zenodo_json(course, team, website),
    )

    readme = root / "README.md"
    current = readme.read_text(encoding="utf-8") if readme.exists() else ""

    _write_if_changed(
        readme,
        update_readme(
            current,
            render_readme_section(course, team, website),
        ),
    )


def citation_text(course, team, website):
    """Return the citation text shown in the README and on the Syllabus page."""

    return _citation_text(course, team, website)
