"""
Generate FAIR metadata for a training instance.

All metadata is generated from the existing data files
(course.yml, team.yml and website.yml), so there is only one
place to edit:

- CITATION.cff       citation metadata (GitHub, reference managers)
- .zenodo.json       metadata for the Zenodo record of each release
- README.md          the generated blocks, when the README has them
- bioschemas.html    Bioschemas JSON-LD for the overview page (e.g. for TeSS)

The generated files should never be edited by hand: they are
overwritten on every render.
"""

import html
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

# Funders whose grants Zenodo can link to, with their funder DOI
# (from the Open Funder Registry). Zenodo only accepts grants from
# these funders: grants from other funders are mentioned in the
# description of the Zenodo record instead.
# Keys are normalised: lower case, without punctuation.
ZENODO_FUNDERS = {
    "european commission": "10.13039/501100000780",
    "ec": "10.13039/501100000780",
    "horizon europe": "10.13039/501100000780",
    "horizon 2020": "10.13039/501100000780",
    "research council of finland": "10.13039/501100002341",
    "academy of finland": "10.13039/501100002341",
    "agence nationale de la recherche": "10.13039/501100001665",
    "australian research council": "10.13039/501100000923",
    "austrian science fund": "10.13039/501100002428",
    "canadian institutes of health research": "10.13039/501100000024",
    "european environment agency": "10.13039/501100000806",
    "fundacao para a ciencia e a tecnologia": "10.13039/501100001871",
    "national health and medical research council": "10.13039/501100000925",
    "national institutes of health": "10.13039/100000002",
    "nih": "10.13039/100000002",
    "national science foundation": "10.13039/100000001",
    "nsf": "10.13039/100000001",
    "nederlandse organisatie voor wetenschappelijk onderzoek": "10.13039/501100003246",
    "nwo": "10.13039/501100003246",
    "schweizerischer nationalfonds": "10.13039/501100001711",
    "swiss national science foundation": "10.13039/501100001711",
    "snsf": "10.13039/501100001711",
    "science foundation ireland": "10.13039/501100001602",
    "uk research and innovation": "10.13039/100014013",
    "ukri": "10.13039/100014013",
    "wellcome trust": "10.13039/100004440",
    "wellcome": "10.13039/100004440",
}

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
    key = language.lower()

    if key in LANGUAGES:
        return LANGUAGES[key]

    # Also accept the codes themselves, e.g. "en" or "eng".
    for tag, code in LANGUAGES.values():
        if key in (tag, code):
            return tag, code

    if re.match(r"^[a-z]{3}$", key):
        return "", key

    return language, ""


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
#
# The README is filled in through named blocks, each marked like:
#
#   <!-- generated:course-information -->
#   <!-- /generated:course-information -->
#
# Only the text between a block's two markers is replaced, so the
# rest of the README can be written by hand. A README without
# markers (such as the template's own README) is left unchanged.

README_BLOCK = re.compile(
    r"(<!-- generated:([a-z-]+) -->\n).*?(<!-- /generated:\2 -->)",
    flags=re.S,
)


def _badge_text(value):
    """Escape text for a shields.io badge."""

    from urllib.parse import quote

    value = value.replace("-", "--").replace("_", "__").replace(" ", "_")

    return quote(value, safe="_.")


def _readme_header(course, team, website):
    """Title, badges and short description."""

    reuse = course.get("reuse") or {}
    doi = _doi(course)
    licence_name = _text(reuse.get("licence")) or licence_id(course)
    link = licence_url(course)

    badges = []

    if doi:
        badges.append(
            f"[![DOI](https://zenodo.org/badge/DOI/{doi}.svg)]"
            f"(https://doi.org/{doi})"
        )

    if licence_name:
        badge = (
            "![Licence](https://img.shields.io/badge/licence-"
            f"{_badge_text(licence_name)}-blue)"
        )
        badges.append(f"[{badge}]({link})" if link else badge)

    lines = [f"# {_text(course.get('title'))}", ""]

    if badges:
        lines += [" ".join(badges), ""]

    if _text(course.get("subtitle")):
        lines += [f"*{_text(course.get('subtitle'))}*", ""]

    if _text(course.get("description")):
        lines += [_text(course.get("description"))]

    return lines


def _readme_course_information(course, team, website):
    """Key facts about this instance of the training."""

    url = website_url(course, website)
    doi = _doi(course)

    facts = [
        ("Course website", f"<{url}>" if url else ""),
        ("Dates", _dates(course)),
        ("Duration", _text(course.get("duration"))),
        ("Mode", _text(course.get("mode"))),
        ("Location", _text(course.get("location"))),
        ("Target audience", _text(course.get("target_audience"))),
        ("Expertise level", _text(course.get("expertise_level"))),
        ("Language", _text(course.get("language"))),
        ("Version", version(course)),
        ("DOI", f"[{doi}](https://doi.org/{doi})" if doi else ""),
    ]

    return ["## Course information", ""] + [
        f"- **{label}:** {value}"
        for label, value in facts
        if value
    ]


def _readme_learning_outcomes(course, team, website):
    """The learning outcomes."""

    outcomes = _list(course.get("learning_outcomes"))

    if not outcomes:
        return []

    return [
        "## Learning outcomes",
        "",
        "After completing this training, participants will be able to:",
        "",
    ] + [f"- {outcome}" for outcome in outcomes]


def _readme_contributors(course, team, website):
    """Everyone in the training team, with role, ORCID and affiliation."""

    members = [
        member
        for member in team.get("members") or []
        if _text(member.get("name"))
    ]

    if not members:
        return []

    def role_rank(member):
        roles = member.get("roles") or []
        ranks = [ROLE_ORDER.index(r) for r in roles if r in ROLE_ORDER]
        return min(ranks) if ranks else len(ROLE_ORDER)

    def cell(value):
        return _text(value).replace("|", "\\|")

    lines = [
        "## Contributors",
        "",
        "| Name | Role | ORCID | Affiliation |",
        "|------|------|-------|-------------|",
    ]

    for member in sorted(members, key=role_rank):
        orcid = _orcid(member.get("orcid"))
        orcid_cell = (
            f"[{orcid.removeprefix('https://orcid.org/')}]({orcid})"
            if orcid else ""
        )

        lines.append(
            f"| {cell(member.get('name'))} "
            f"| {cell(', '.join(member.get('roles') or []))} "
            f"| {orcid_cell} "
            f"| {cell(member.get('affiliation'))} |"
        )

    return lines


def _readme_citation(course, team, website):
    """How to cite the training."""

    return [
        "## Citation",
        "",
        "If you use these materials, please cite them as:",
        "",
        f"> {_citation_text(course, team, website)}",
        "",
        "Citation metadata is available in [CITATION.cff](CITATION.cff).",
    ]


def _readme_licence(course, team, website):
    """The licence of the training materials."""

    reuse = course.get("reuse") or {}
    licence_name = _text(reuse.get("licence")) or licence_id(course)
    link = licence_url(course)

    if licence_name and link:
        text = (
            "Unless otherwise stated, the training materials are "
            f"licensed under [{licence_name}]({link})."
        )
    elif licence_name:
        text = (
            "Unless otherwise stated, the training materials are "
            f"licensed under {licence_name}."
        )
    else:
        text = "See [LICENSE](LICENSE)."

    return ["## Licence", "", text]


def _readme_acknowledgements(course, team, website):
    """Funding, when given in course.yml."""

    entries = funding(course)

    if not entries:
        return []

    return [
        "## Acknowledgements",
        "",
        "This training was funded by:",
        "",
    ] + [f"- {_funding_text(entry)}" for entry in entries]


README_BLOCKS = {
    "header": _readme_header,
    "course-information": _readme_course_information,
    "learning-outcomes": _readme_learning_outcomes,
    "contributors": _readme_contributors,
    "citation": _readme_citation,
    "licence": _readme_licence,
    "acknowledgements": _readme_acknowledgements,
}


def update_readme(text, course, team, website):
    """
    Fill in the generated blocks of a README.

    Blocks with an unknown name are left unchanged, and so is a
    README without any blocks. A block whose data is missing
    (for example no funding) is emptied, heading included.
    """

    def fill(match):
        start, name, end = match.group(1), match.group(2), match.group(3)
        render = README_BLOCKS.get(name)

        if render is None:
            return match.group(0)

        lines = render(course, team, website)
        body = "\n".join(lines) + "\n" if lines else ""

        return start + body + end

    return README_BLOCK.sub(fill, text)


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


# Zenodo contributor type for each team role. The first matching
# role in ROLE_ORDER is used.
ZENODO_CONTRIBUTOR_TYPES = {
    "Training lead": "ProjectLeader",
    "Instructor": "ProjectMember",
    "Contributor": "Other",
}


def _zenodo_contributors(team):
    """
    Return the team members left out of the citation
    (citation_author: false) as Zenodo contributors.

    They are shown on the Zenodo record, but are not part of
    the citation.
    """

    contributors = []

    for member in team.get("members") or []:
        if member.get("citation_author", True) is not False:
            continue

        if not _text(member.get("name")):
            continue

        roles = member.get("roles") or []

        contributor_type = next(
            (
                ZENODO_CONTRIBUTOR_TYPES[role]
                for role in ROLE_ORDER
                if role in roles
            ),
            "Other",
        )

        contributor = _zenodo_creator(member)
        contributor["type"] = contributor_type
        contributors.append(contributor)

    return contributors


def funding(course):
    """
    Return the funding entries from course.yml as a list of
    dictionaries with funder, grant_number and grant_title.
    """

    entries = []

    for entry in course.get("funding") or []:
        if not isinstance(entry, dict):
            continue

        funder = _text(entry.get("funder"))

        if not funder:
            continue

        entries.append({
            "funder": funder,
            "grant_number": _text(entry.get("grant_number")),
            "grant_title": _text(entry.get("grant_title")),
        })

    return entries


def _zenodo_funder_doi(funder):
    """Return the funder DOI when Zenodo supports the funder."""

    key = re.sub(r"[^a-z0-9 ]", "", funder.lower()
                 .replace("ã", "a").replace("ç", "c"))

    return ZENODO_FUNDERS.get(" ".join(key.split()), "")


def _zenodo_grants(course):
    """Return the grants Zenodo can link to."""

    grants = []

    for entry in funding(course):
        funder_doi = _zenodo_funder_doi(entry["funder"])

        if funder_doi and entry["grant_number"]:
            grants.append(
                {"id": f"{funder_doi}::{entry['grant_number']}"}
            )

    return grants


def _funding_text(entry):
    """Return a funding entry as one line of text."""

    text = entry["funder"]

    if entry["grant_title"]:
        text += f", {entry['grant_title']}"

    if entry["grant_number"]:
        text += f" (grant {entry['grant_number']})"

    return text


def render_zenodo_json(course, team, website):
    """
    Return the contents of .zenodo.json.

    Zenodo's GitHub integration reads this file when a release is
    published, and uses it for the new version of the Zenodo record.
    It takes precedence over CITATION.cff.
    """

    reuse = course.get("reuse") or {}
    url = website_url(course, website)

    funded_by = [_funding_text(entry) for entry in funding(course)]

    description = [
        f"<p>{html.escape(_text(course.get('description')))}</p>"
        if _text(course.get("description")) else "",
        f"<p>Training dates: {_dates(course)}.</p>"
        if _dates(course) else "",
        f'<p>Training website: <a href="{html.escape(url)}">'
        f"{html.escape(url)}</a></p>"
        if url else "",
        "<p>Funded by: "
        + "; ".join(html.escape(text) for text in funded_by)
        + ".</p>"
        if funded_by else "",
    ]

    data = {
        "title": _text(course.get("title")),
        "upload_type": "lesson",
        "description": "\n".join(part for part in description if part),
        "creators": [_zenodo_creator(member) for member in authors(team)],
        "contributors": _zenodo_contributors(team),
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
        "grants": _zenodo_grants(course),
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
        "funder": [
            {"@type": "Organization", "name": entry["funder"]}
            for entry in funding(course)
        ],
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
    Write CITATION.cff and .zenodo.json to the repository root,
    and fill in the generated blocks of README.md.
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

    # Only fill in the README when it has generated blocks, so the
    # template's own README is never changed.
    readme = root / "README.md"

    if readme.exists():
        _write_if_changed(
            readme,
            update_readme(
                readme.read_text(encoding="utf-8"),
                course,
                team,
                website,
            ),
        )


def citation_text(course, team, website):
    """Return the citation text shown in the README and on the Syllabus page."""

    return _citation_text(course, team, website)
