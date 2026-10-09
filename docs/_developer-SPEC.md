# Training Instance Developer Specification

This document describes the technical architecture, data model, validation, generated files, FAIR metadata and deployment of a **training instance branch** (`release-YYMM`).

It is intended for developers and maintainers of the SciLifeLab Training Webpage Template. Instructions for training organisers are provided in the [User Guide](https://scilifelab-training.github.io/scilifelab-course-webpage-template-user-guide/). The landing page is documented separately in `docs/developer/landing-runbook.md` on the `main` branch.

This document describes implemented behaviour, not planned functionality. For exact behaviour, the code in `scripts/` and the authored `.qmd` files is authoritative. Keep this document in sync when that code changes (see [section 17](#17-keeping-this-specification-current)).

## 1. Architecture overview

The published website consists of two layers:

- the **landing page**, built from `main` and published at the root of the website;
- individual **training instances**, each built from a `release-YYMM` branch and published in its own subdirectory.

| Branch | Purpose | Published location |
|---|---|---|
| `main` | Landing page source | `/` |
| `release-0000` | Template for new training instances | `/0000/` |
| `release-YYMM` | Source for one training instance | `/YYMM/` |
| `gh-pages` | Machine-managed published output | Entire published website |

A training instance is one time a training is given. Each instance is self-contained: it has its own data files, content pages and generated metadata, and is deployed independently of the landing page and of other instances.

> [!IMPORTANT]
> Do not edit `gh-pages` directly during normal development. It contains machine-managed published output. Manual changes should only be made as part of a targeted recovery procedure (see [section 16](#16-deployment-recovery)).

### 1.1 Design principles

1. **One source of truth.** Structured information lives in `data/*.yml`. Renderers derive pages, navigation and metadata files from it, so a value is edited in one place only.
2. **Separate data from presentation.** YAML describes information, Python processes it, Quarto composes pages, and CSS and JavaScript provide presentation and interaction.
3. **Keep learning content flexible.** Authors choose their own content structure in `content/`, written in plain Markdown.
4. **Make optionality explicit.** Optional information is left out of pages and metadata when it is empty, rather than shown as empty sections.
5. **FAIR by default.** Citation, archiving and discovery metadata are generated from the same data as the website, so they cannot drift apart.

### 1.2 What training organisers edit

Training organisers only edit:

| What | Where |
|---|---|
| Training information | `data/*.yml` |
| Training materials | `content/` |
| Images, such as team photos and logos | `img/` |
| A few hand-written README sections | `README.md`, based on `docs/_template-README.md` |

Everything else (renderers, styles, scripts and workflows) is template code, maintained by template developers.

## 2. Repository structure

```text
release-YYMM/
├── .github/workflows/main.yml   # Instance deployment
├── _generated/                  # Generated fragments (build output)
├── _sections/                   # Reusable page sections (navbar, footer, ...)
├── _site/                       # Rendered website (build output)
├── content/
│   ├── _metadata.yml            # Settings for all content pages
│   ├── index.qmd                # Content introduction page
│   └── module-1/ ...            # One folder per content section
├── data/
│   ├── announcements.yml
│   ├── course.yml
│   ├── faq.yml
│   ├── practicalities.yml
│   ├── preparation.yml
│   ├── resources.yml
│   ├── schedule.yml
│   ├── team.yml
│   └── website.yml
├── docs/
│   ├── _developer-SPEC.md       # This document
│   └── _template-README.md      # README template for training instances
├── img/
├── js/schedule.js               # Schedule and "Next up" behaviour
├── scripts/
│   ├── content.py               # Content section and page loading
│   ├── loaders.py               # YAML loading
│   ├── render_course.py         # Pre-render entry point
│   ├── utils.py
│   ├── validators.py            # Data validation
│   ├── writer.py                # Writes generated fragments
│   └── renderers/               # One renderer per page or component
├── *.qmd                        # Page shells (index, schedule, syllabus, ...)
├── _quarto.yml
├── styles.css
├── requirements.txt
├── CITATION.cff                 # Generated
├── .zenodo.json                 # Generated
├── CONTRIBUTING.md
├── LICENSE.md
└── README.md                    # Partly generated (see section 13.4)
```

Only the pages in the `render` list of `_quarto.yml` are built: `index.qmd`, the page shells and `content/`. Files and folders starting with `_` or `.` are never rendered by Quarto, so the documentation files in `docs/` also start with an underscore as an extra safeguard. Other files in `docs/`, such as the example image, PDF and video, are copied to the website because content pages link to them.

## 3. Render flow

The website is rendered as part of the Quarto build:

1. `quarto render` starts and runs `scripts/render_course.py` as a pre-render step.
2. `render_course.py` deletes and recreates `_generated/`.
3. The data files are loaded (`loaders.py`) and the content sections are read (`content.py`).
4. Team members without a `name` get one built from `given_names` and `family_names` (`complete_names`).
5. Course, website, schedule and team data are validated (`validators.py`). Invalid data stops the render with an explanatory error.
6. `available_pages` is calculated (see [section 5](#5-page-availability-and-navigation)).
7. The renderers write fragments to `_generated/`.
8. `renderers/fair.py` writes `CITATION.cff` and `.zenodo.json` to the repository root, and fills in the generated blocks of `README.md`.
9. Quarto renders the page shells, which include the generated fragments, into `_site/`.

```text
data/*.yml + content/
        │
        ▼
loaders.py + content.py ──> complete_names ──> validators.py
                                                    │
                                                    ▼
                                             render_course.py
                                                    │
                        ┌───────────────────────────┴──────────────────────┐
                        ▼                                                  ▼
               scripts/renderers/                                  renderers/fair.py
                        │                                                  │
                        ▼                                                  ▼
                 _generated/*                        CITATION.cff, .zenodo.json, README.md
                        │                              (repository root)
                        ▼
          *.qmd page shells + _sections/
                        │
                        ▼
                     Quarto ──> _site/
```

### 3.1 Generated fragments

| Fragment | Renderer | Used by |
|---|---|---|
| `navbar_meta.qmd`, `navbar_brand.qmd`, `navbar_links.qmd` | `navbar.py` | Navbar on all normal pages |
| `welcome.qmd` | `welcome.py` | Overview |
| `registration.qmd` | `registration.py` | Overview |
| `upcoming.qmd` | `upcoming.py` | Overview |
| `quick_links.qmd` | `quick_links.py` | Overview |
| `announcements.qmd`, `announcements_page.qmd` | `announcements.py` | Overview, Announcements |
| `team.qmd`, `team_page.qmd` | `team.py`, `team_page.py` | Overview, Team |
| `schedule.qmd` | `schedule.py` | Schedule |
| `syllabus.qmd` | `syllabus.py` | Syllabus |
| `practicalities.qmd`, `preparation.qmd`, `faq.qmd`, `resources.qmd` | one renderer each | Information pages |
| `footer.qmd` | `footer.py` | All normal pages |
| `content-navbar.html`, `content-next-navigation.html`, `content-footer.html` | `content.py` | Content pages |
| `bioschemas.html` | `fair.py` | Overview (`<head>`) |

Do not edit files in `_generated/`. They are overwritten on every render.

## 4. Data files

| Data file | Purpose | Required? |
|---|---|---|
| `course.yml` | Training identity, delivery, educational information, administration, reuse and DOIs | Yes |
| `team.yml` | People, roles and contact information | Yes |
| `website.yml` | Navbar logos, welcome, registration, quick links, footer and content sections | Yes |
| `schedule.yml` | Scheduled events | File required; may contain `events: []` |
| `announcements.yml` | Announcements | File required; may be empty |
| `preparation.yml`, `practicalities.yml`, `faq.yml`, `resources.yml` | Information pages | File required; content optional |

The loaders open the YAML files by name, so keep every file in the repository. "Optional" means that the corresponding page or section can be empty, not that the file can be deleted.

### 4.1 `course.yml`

| Field | Required | Used for |
|---|---|---|
| `title`, `description` | Yes | Website, Syllabus, README, citation, Zenodo, Bioschemas |
| `mode` | Yes | Syllabus, Bioschemas `courseMode` |
| `location` | Yes | Website, Syllabus, Bioschemas `location` (required by Bioschemas). Use `"Online"` for online or self-paced training |
| `language` | Yes | Syllabus, Zenodo (ISO 639-3), Bioschemas (BCP 47). Accepts a language name or code |
| `target_audience` | Yes | Syllabus, README, Bioschemas |
| `learning_outcomes` | Yes, non-empty list | Syllabus, README, Bioschemas `teaches` |
| `keywords` | Yes, list | Syllabus, README, citation, Zenodo, Bioschemas (required by Bioschemas) |
| `organizers` | Yes, non-empty list | Syllabus, Bioschemas `provider` and `organizer` |
| `contact.email` | Yes | Contact boxes on the Preparation and Practicalities pages |
| `subtitle`, `duration`, `instruction`, `credits`, `expertise_level`, `prerequisites`, `examination`, `content_providers` | No | Syllabus; some also README and Bioschemas |
| `start_date`, `end_date` | No | Website, Syllabus, README, Zenodo description, Bioschemas. Omit for self-paced training |
| `funding` | No | Syllabus, README, Zenodo, Bioschemas (see [section 13.5](#135-funding)) |
| `reuse` | No | Licence, DOIs and citation (see [section 13](#13-fair-metadata)) |

Dates use `YYYY-MM-DD`.

### 4.2 `team.yml`

| Field | Required | Notes |
|---|---|---|
| `given_names`, `family_names` | Yes | Used for the citation and Zenodo. The display `name` is built from them |
| `roles` | Yes, non-empty list | `Training lead`, `Instructor` and/or `Contributor` |
| `affiliation` | Yes | |
| `email` | No | Required when `course_contact: true` |
| `course_contact` | No | At least one member must have `course_contact: true` and an email |
| `orcid` | No | Full URL or bare ORCID; validated |
| `citation_author` | No | `false` leaves the person out of the citation; they become a Zenodo contributor instead (default `true`) |
| `job_title`, `bio`, `linkedin`, `github`, `website`, `image` | No | Team page; `image` also on the Overview team preview |

These fields belong to each entry in `team.members`. An optional `team.intro` is shown at the top of the Team page.

A `name` field is still accepted for older data files. In that case the last word is used as the family name.

### 4.3 `website.yml`

Contains the navbar logos, welcome section, registration banner, quick-link page definitions, footer and content sections. Two parts are used beyond the website itself:

- `footer.repository.url` is used to work out the website address of the instance (see [section 13.1](#131-instance-identity)). The validator requires it to be a GitHub repository address (`https://github.com/<owner>/<repo>`).
- `pages` must keep all seven keys (`content`, `syllabus`, `schedule`, `practicalities`, `preparation`, `resources`, `faq`), because the quick-links renderer reads them directly.

The top-level `content` mapping in the same file defines the content sections (see [section 8.1](#81-structure)).

## 5. Page availability and navigation

`render_course.py` calculates `available_pages`, which controls which optional pages appear in the navbar.

| Page | Availability |
|---|---|
| Overview, Content, Syllabus, Team | Always |
| Schedule | When `schedule.yml` contains events |
| Practicalities | When practicalities data is not empty |
| Preparation | When `preparation.yml` has `sections` |
| FAQ, Resources | When their data is not empty |
| Announcements | When `announcements.yml` contains items |

"Not empty" means that the top-level mapping or list in the file contains anything, including placeholder text. To hide an optional page, empty its data (for example `faq: {}`).

Navbar structure: Overview, Content, Schedule (when available), and an Information dropdown with Preparation, Practicalities, Announcements, Resources, Team, Syllabus and FAQ (each when available).

The quick links on the Overview page use the same `available_pages` (see [section 6.4](#64-quick-links)). Deleting an optional `.qmd` file does not remove the page from the navbar or the quick links; it only breaks the link.

## 6. Overview page

The Overview page (`index.qmd`) includes these sections in order.

### 6.1 Welcome

Title, dates and location from `course.yml`; welcome title, text and image from `website.yml`. Dates and location are only shown when provided.

### 6.2 Registration banner

| Configuration or state | Result |
|---|---|
| `enabled: false`, or no `opening_date` | No banner |
| Before `opening_date` | "Registration opens soon" with the date |
| Open (on or after opening, before or on closing) | Deadline, fee and link; requires `url` |
| After `closing_date`, `after_closing: "closed"` | Closed message |
| After `closing_date`, `after_closing: "hide"` or omitted | No banner |

A fee is shown when both `cost.amount` and `cost.currency` are given; `cost.note` can be shown on its own.

> [!IMPORTANT]
> The banner state is decided when the site is rendered, not in the browser. The banner only changes from "opens soon" to "open" to "closed" after the next render, so push a change (or re-run the workflow) on or after the opening and closing dates.

### 6.3 Next up

Rendered when `schedule.yml` has events. `js/schedule.js` shows the first event whose end time is in the future, with a countdown, and updates every second. An event with `content` links to its content page.

### 6.4 Quick links

Up to four cards, in this priority: Content, Syllabus, Schedule, Practicalities, Preparation, Resources, FAQ. Content and Syllabus are always shown; the others only when they are in `available_pages`, so a quick link never points to a page that is missing from the navbar. Titles, descriptions, icons and links come from `website.pages`.

### 6.5 Announcements and team preview

Announcements show the two newest items, or "No active announcements." The team preview shows up to two people: training leads first, then instructors. Contributors are not shown.

### 6.6 Bioschemas markup

`index.qmd` includes `_generated/bioschemas.html` in its `<head>` (see [section 13.3](#133-bioschemas)). No other page has the markup.

## 7. Schedule

Each event in `schedule.yml` has `title`, `type`, `group`, `start`, `end`, `location` and `people`, and optionally `content`. The schedule validator only checks that `events` is a list; a missing field stops the render with a Python error.

`start` and `end` use `YYYY-MM-DDTHH:MM` **without quotes**, so YAML reads them as date-times. A quoted time is read as text and breaks the schedule and "Next up" renderers.

Events are sorted by `start` and grouped by `group`. The Schedule page shows the training dates and location at the top, a list of groups on the left, and one group at a time on the right; the first group is shown when the page opens (`js/schedule.js`). Each group is labelled with its name and the date of its first event.

### 7.1 Event types

Supported types: `lecture`, `workshop`, `practical`, `discussion`, `break`, `welcome`, `lunch`, `presentation`, `assessment`, `group-work`, `exercise`, `consultation`, `quiz`, `feedback`, `seminar`.

Underscores in a type are converted to hyphens. Each type has a `.course-type-<type>` class in `styles.css` that only sets two variables:

```css
.course-type-workshop {
    --course-type-bg: #eef6e8;
    --course-type-color: #5f7f15;
}
```

Both the badge and the timeline dot read these variables. The schedule renderer puts the type class on both the badge and the event row. To add a type, add one class with its two variables. Unknown types get a grey badge.

### 7.2 Timeline layout

The time column width, row padding and dot size are CSS variables on `.course-schedule-event`. The position of the timeline dots and lines is calculated from them, so changing the column width or padding moves the timeline automatically.

## 8. Content pages

### 8.1 Structure

`website.yml` defines the content sections:

```yaml
content:
  sections:
    - id: module-1          # folder name in content/
      label: "Module 1"     # shown in the content navigation
      title: "Introduction" # tooltip
```

Each `id` must match a folder in `content/`; a missing folder stops the render. Only `.qmd` files directly inside a section folder are read, not files in subfolders. Every page needs a `title` in its front matter. Pages are sorted by `order` (a whole number) in their front matter, or alphabetically by filename when no page in the section has `order`. Mixing ordered and unordered pages in one section is an error.

The previous/next links at the bottom of each page follow one sequence through all content: `content/index.qmd` (labelled "Introduction") first, then the pages of each section in the configured order.

### 8.2 How content pages are built

Content pages are plain Markdown, so the site chrome is added through `content/_metadata.yml`:

```yaml
format:
  html:
    toc: true
    toc-depth: 2
    toc-location: right
    toc-title: "On this page"
include-before-body:
  - ../_generated/content-navbar.html
include-after-body:
  - ../_generated/content-next-navigation.html
  - ../_generated/content-footer.html
```

`content-navbar.html` contains the navbar, the grey content navigation and a script that:

- moves the navbar, footer and previous/next links out of Quarto's table-of-contents grid, so they span the same width as on normal pages;
- sets the links and the active state of the navbar, content navigation and previous/next links. Content pages sit at different folder depths, so links and images (`data-course-asset`) are made absolute from the part of the address before `/content/`;
- handles the content navigation dropdowns;
- keeps the table of contents highlighting in step with clicks.

Only `##` headings appear in the table of contents (`toc-depth: 2`).

### 8.3 Content navigation

The grey content navigation scrolls sideways when the modules do not fit. Because a scrolling container clips its children, the dropdown menus use `position: fixed` and are placed under their button by JavaScript. They are repositioned on scroll and resize.

- **Hover** opens a menu for mouse users only; touch and keyboard users open it with a click or tap.
- **Fades and arrows** appear at an edge when there are more modules in that direction (classes `can-scroll-left` and `can-scroll-right`).
- **On load**, the current module is scrolled into view.

## 9. Syllabus

Generated from `course.yml` and `team.yml`. Sections are shown only when they have content:

| Section | Content |
|---|---|
| Header | Title, subtitle |
| Abstract | Description, keywords |
| Details | Dates, duration, delivery, location, language, credits |
| Learning outcomes | Numbered list |
| Target audience | Audience, expertise level |
| Prerequisites | Knowledge and technical |
| Forms of instruction and examination | Instruction, examination |
| Administration | Organisers, content providers, funders; training leads with affiliation and email |
| Reuse | Licence, DOI, citation |

The DOI and citation are the same as in `CITATION.cff` and the README: the Syllabus uses `concept_doi`, `version_doi` and `citation_text` from `fair.py`.

## 10. Information pages

| Page | Data | Notes |
|---|---|---|
| Preparation | `preparation.yml` | Sections with blocks: `text`, `checklist`, `account`, `hardware`, `software`, `reading`, `callout` (`important`, `note` or `warning`). Consecutive `account` and `software` blocks form grids. Unknown block types are ignored |
| Practicalities | `practicalities.yml` | `intro`, `venue` (with OpenStreetMap embed from `map_url`), `transport`, `accommodation`, `food`, `additional` |
| Announcements | `announcements.yml` | All items, newest first |
| Resources | `resources.yml` | Fixed categories, each a list of titled links |
| Team | `team.yml` | Grouped by role: training leads, instructors, contributors. A person with several roles appears in each group. Course contacts are marked |
| FAQ | `faq.yml` | Accordion |

All information pages share the page header classes (`.course-page-label`, `.course-page-title`, `.course-page-intro`). Preparation and Practicalities share the contact box (`.course-page-contact`).

## 11. Styling

`styles.css` is organised by component and page, with the responsive rules at the end.

### 11.1 Design variables

Defined in `:root`:

| Variable | Purpose |
|---|---|
| `--course-shell-max-width`, `--course-shell-gutter` | Width and side space of navbar, content and footer, on normal and content pages alike |
| `--course-content-padding` | Horizontal padding inside sections; `0.2rem` below 750px |
| `--course-color-primary`, `-link`, `-accent`, `-text`, `-muted` | Main colours |
| `--course-color-border`, `-border-light`, `-surface` | Borders and background surfaces |

Changing a colour or the page width in `:root` updates the whole site.

### 11.2 Shared classes

| Class | Purpose |
|---|---|
| `.course-text-link` | Standard text link with hover underline |
| `.course-page-label`, `.course-page-title`, `.course-page-intro`, `.course-page-intro-narrow` | Information page headers |
| `.course-page-contact` | Contact box |
| `.course-type-*` | Event type colours (see [section 7.1](#71-event-types)) |

### 11.3 Breakpoints

| Width | Purpose |
|---|---|
| 1100px | Large tablets and small laptops |
| 850px | Tablets: two-column layouts become one column |
| 750px | Mobile: page layout, navbar and footer go full width |
| 600px | Small mobile: compact spacing |
| 450px | Very small mobile |

Navbar-specific exceptions: 950px (full logo to symbol logo) and 751px–1200px (extra space beside the navbar title). Use the standard widths for new rules.

## 12. Validation

`validators.py` stops the render with a message that explains how to fix the data.

**`course.yml`**

- The required fields in [section 4.1](#41-courseyml) must be present; `learning_outcomes` and `organizers` must be non-empty lists, and `contact` a mapping with an `email`.
- `start_date`, `end_date` and `reuse.release_date`, when given, must be valid `YYYY-MM-DD` dates, and `end_date` must not be before `start_date`.
- `reuse.doi` and `reuse.version_doi`, when given, must be valid DOIs (bare, `doi:` or `https://doi.org/` form).

**`team.yml`**

- At least one member is required. Every member needs a name, a non-empty `roles` list with only allowed roles, and an `affiliation`.
- `orcid`, when given, must be a valid ORCID.
- At least one member needs `course_contact: true` and an email, and a contact without an email is an error.

**`website.yml`**

- The `content` and `syllabus` page entries must exist.
- `footer.repository.url` must be a GitHub repository address.

**`schedule.yml`**

- `events` must be a list. Individual events are not validated.

Funding is not validated: an entry without a funder is skipped.

## 13. FAIR metadata

All FAIR metadata is generated by `scripts/renderers/fair.py` from `course.yml`, `team.yml` and `website.yml`.

| Output | Location | Purpose |
|---|---|---|
| `CITATION.cff` | Repository root | Citation metadata for GitHub and reference managers |
| `.zenodo.json` | Repository root | Metadata for the Zenodo record of each release |
| Bioschemas JSON-LD | `_generated/bioschemas.html`, in the Overview `<head>` | Discovery by training registries such as ELIXIR TeSS |
| Generated README blocks | `README.md` | Training information for people browsing the repository |

Files are only rewritten when their content changes, so a render without data changes produces no new commit.

### 13.1 Instance identity

| Value | Derived from |
|---|---|
| Instance id (`YYMM`) | The `release-YYMM` branch name (`GITHUB_REF_NAME` in GitHub Actions, otherwise the local Git branch) |
| Instance website | `https://<owner>.github.io/<repo>/YYMM/`, from `footer.repository.url`; overridden by `reuse.website_url` |
| Training (landing page) website | The instance website without `YYMM/` |
| Version | `reuse.version`, or the instance id |

When the branch name does not match `release-YYMM` (for example on a feature branch), the instance id and website URL are empty, and the outputs fall back to the repository URL.

### 13.2 DOIs and citation

Each training has one **concept DOI** (`reuse.doi`), which always resolves to the latest instance. Each published instance has its own **version DOI** (`reuse.version_doi`) and `reuse.release_date`, added after its Zenodo release.

- **The most specific DOI** (the version DOI if set, otherwise the concept DOI) is used in `CITATION.cff` (`doi`), the README badge, the README citation and the Syllabus.
- **When both DOIs are set**, `CITATION.cff` lists both under `identifiers`.
- **Authors** are team members ordered training leads, instructors, contributors, excluding those with `citation_author: false`. Duplicate names are listed once.
- **The citation text** is `reuse.preferred_citation` when set, otherwise "Family, I.; Family, I. (year). Title. Version YYMM. DOI or website", with the year taken from `release_date`.
- **The licence identifier** (SPDX, for example `CC-BY-4.0`) comes from `reuse.licence_id`, or is recognised from `reuse.licence`.

### 13.3 Bioschemas

The markup follows the Bioschemas [Course](https://bioschemas.org/profiles/Course/1.0-RELEASE) and [CourseInstance](https://bioschemas.org/profiles/CourseInstance/1.0-RELEASE) profiles: one Course, with this instance nested in `hasCourseInstance`.

All instances of a training share the same Course `@id`: the concept DOI (`https://doi.org/...`) when set, otherwise the landing page address with `#course`. Registries therefore recognise every instance as a run of the same course. The CourseInstance `@id` is the instance website with `#course-instance`.

| Course field | Source |
|---|---|
| `name`, `description`, `keywords` | `title`, `description`, `keywords` (all required by Bioschemas) |
| `url` | Landing page website |
| `identifier` | Concept DOI |
| `license` | `reuse.licence_url` |
| `educationalLevel`, `teaches`, `coursePrerequisites`, `audience` | `expertise_level`, `learning_outcomes`, `prerequisites`, `target_audience` |
| `provider` | `organizers` |
| `creator` | Citation authors |

| CourseInstance field | Source |
|---|---|
| `courseMode`, `location` | `mode`, `location` (both required by Bioschemas) |
| `startDate`, `endDate` | `start_date`, `end_date` |
| `inLanguage` | `language`, as a BCP 47 tag |
| `identifier` | Version DOI |
| `instructor` | All training leads and instructors, including those with `citation_author: false` |
| `organizer`, `funder` | `organizers`, `funding` |
| `url` | Instance website |

Empty values are left out. Test the markup with [validator.schema.org](https://validator.schema.org/) or the TeSS Bioschemas testing tool.

### 13.4 Zenodo and README

**`.zenodo.json`** takes precedence over `CITATION.cff` when Zenodo archives a GitHub release:

| Field | Source |
|---|---|
| `title`, `keywords`, `version` | `title`, `keywords`, version |
| `upload_type` | `lesson` (fixed) |
| `description` | Description, training dates, website link, and funders (HTML) |
| `creators` | Citation authors, with affiliation and ORCID |
| `contributors` | Members with `citation_author: false`; type from their role (`ProjectLeader`, `ProjectMember` or `Other`) |
| `license` | SPDX identifier, lower case |
| `language` | ISO 639-3 code |
| `related_identifiers` | Instance website (`isSupplementedBy`) |
| `communities` | `reuse.zenodo_communities` |
| `grants` | Funding from funders that Zenodo supports (see [section 13.5](#135-funding)) |

**`README.md`** is filled in through named blocks:

```markdown
<!-- generated:contributors -->
<!-- /generated:contributors -->
```

Only the text between a block's markers is replaced. Supported blocks: `header`, `course-information`, `learning-outcomes`, `contributors`, `citation`, `licence`, `acknowledgements`. A block whose data is missing is emptied, heading included. A README without markers is never changed. That is why the template's own README on `release-0000` stays as it is, while a README based on `docs/_template-README.md` is filled in.

### 13.5 Funding

`course.funding` is an optional list of `funder`, `grant_number` and `grant_title`. Every funder appears on the Syllabus, in the README acknowledgements, in the Zenodo description and as Bioschemas `funder`.

Zenodo can only link grants from a fixed list of funders, identified by their funder DOI. `fair.py` adds a grant to `.zenodo.json` `grants` only when it recognises the funder name (`ZENODO_FUNDERS`) and a grant number is given, because an unsupported grant would make Zenodo reject the release. Other funders only appear in the description.

## 14. GitHub Actions

`.github/workflows/main.yml` runs on pushes to `release-*` branches, and can be started by hand (`workflow_dispatch`). It runs on `ubuntu-22.04` in the shared `deploy-gh-pages` concurrency group, together with the landing page deployment:

1. Check out the release branch.
2. Check that the branch name is `release-YYMM` and derive the output directory (`YYMM`).
3. Set up Python 3.12 and install `requirements.txt` (PyYAML).
4. Set up Quarto 1.3.340 (pinned, the same as on `main`).
5. Render the instance site (`quarto render`, which runs the pre-render script).
6. Commit changed generated metadata files (`CITATION.cff`, `.zenodo.json`, `README.md`) back to the branch. Commits pushed with the workflow token do not trigger a new run.
7. Check out `gh-pages`, replace `gh-pages/YYMM/` with `_site/`, and keep `.nojekyll`.
8. Commit and push to `gh-pages`, if anything changed.

Local development uses the same versions: Python 3.12 with `requirements.txt`, and Quarto 1.3.340.

The instance deployment only writes to its own `gh-pages/YYMM/` directory. It never changes the landing page or other instances.

## 15. Publishing a release on Zenodo

1. **One-time setup:** a repository owner switches the repository on in the GitHub section of their Zenodo account.
2. Push the `release-YYMM` branch and wait for the workflow to finish, so `.zenodo.json` is up to date.
3. Create a GitHub release from that branch, with a tag such as `v2505`. Zenodo archives it and assigns a version DOI.
4. Add the concept DOI to `reuse.doi` after the first release only, and the version DOI and date to `reuse.version_doi` and `reuse.release_date`.

When a new instance is branched from an earlier one, empty `version_doi` and `release_date`. Never create a release from `release-0000` or `main`: it would become a version of the training on Zenodo.

## 16. Deployment recovery

If an instance deployment fails or publishes incorrect output:

1. Fix the problem on the `release-YYMM` branch and push again. The workflow replaces `gh-pages/YYMM/` completely.
2. If incorrect files were written outside `gh-pages/YYMM/`, remove only those files in a targeted cleanup commit on `gh-pages`.
3. Check that the landing page and other `gh-pages/YYMM/` directories are intact.

If the "Commit generated metadata files" step fails because the branch changed in the meantime, re-run the workflow.

## 17. Keeping this specification current

Update this document when a change affects:

- YAML field names, requiredness or validation;
- page availability, navbar or quick-link behaviour;
- renderer inputs or outputs, or generated files;
- the content page structure or navigation;
- schedule event types;
- FAIR metadata mappings;
- the deployment workflow.

## 18. Related documentation

- [User Guide](https://scilifelab-training.github.io/scilifelab-course-webpage-template-user-guide/): instructions for training organisers.
- `docs/developer/landing-runbook.md` on `main`: landing page architecture and deployment.
- `docs/developer/landing-migration-map.md` on `main`: mapping of the legacy landing page configuration.
- `docs/_template-README.md`: README template for training instances.
- `CONTRIBUTING.md`: how to contribute to the training materials.