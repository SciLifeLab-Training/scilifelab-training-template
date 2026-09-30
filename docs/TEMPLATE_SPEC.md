# SciLifeLab Training Website Template Specification

**Status:** Working specification  
**Purpose:** Describe the behaviour of the current repository, including its data files, renderers, authored Quarto pages, and generated output.

This document describes implemented behaviour, not planned functionality. Where behaviour is controlled by a renderer or page rather than a YAML flag, that distinction is stated explicitly.

---

## 1. Purpose

The SciLifeLab Training Website Template provides a reusable framework for creating FAIR, maintainable, and consistent training websites using **Quarto** and **GitHub Pages**.

The template is designed to support a broad range of educational formats, including:

- Self-paced online training
- Instructor-led workshops
- Hybrid training
- Multi-day events
- Modular learning resources

The template emphasizes:

- **Single source of truth:** structured information is maintained in data files and reused by the site.
- **FAIR metadata:** training information can be described in a structured, reusable way.
- **Minimal duplication:** renderers derive repeated interface elements from the same data.
- **Consistent user experience:** shared navigation, page patterns, and visual styling.
- **Flexible learning content:** authors choose a content structure that fits the training.

The specification describes the current repository behaviour. It is not a promise that every possible configuration or future feature is implemented.

### 1.1 Glossary

| Term | Meaning |
|---|---|
| Training | The educational offering represented by a website |
| Event | A scheduled item in `schedule.yml` |
| Content section | A configured group of learning pages, such as a module or day |
| Page | A rendered website page, usually authored as a `.qmd` file |
| Renderer | Python code that reads data and produces Quarto fragments or page content |
| Generated fragment | A build-time file produced by a renderer; do not edit directly |

### 1.2 Design principles

The implementation follows these principles:

1. **One authoritative source for structured data.** Data files feed the renderers and reduce repeated manual edits.
2. **Derive interface elements from data.** Navigation availability, quick links, schedule displays, and team previews are generated where supported by the renderers.
3. **Separate data from presentation.** YAML describes structured information; Python processes it; Quarto composes pages; CSS and JavaScript provide presentation and interaction.
4. **Keep learning content flexible.** Authors define their own content sections and pages rather than following a fixed pedagogical model.
5. **Make optionality explicit.** Some pages depend on data availability, while others are always included. A page's presence in the repository is not always the same as its visibility in the site.

## 2. Repository structure

The following reflects the repository provided for this review. The contents of collapsed folders are shown only where relevant.

```text
scilifelab-training-template/
├── _generated/                 # Generated Quarto/HTML fragments
├── _sections/                  # Reusable homepage sections
├── _site/                      # Rendered website
├── .github/
├── .quarto/
├── content/
│   ├── module-1/
│   ├── module-2/
│   ├── module-3/
│   ├── _metadata.yml
│   └── index.qmd
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
├── docs/                       # Example/downloadable files and specifications
├── img/
├── js/
│   └── schedule.js
├── scripts/
│   ├── renderers/
│   ├── content.py
│   ├── loaders.py
│   ├── render_course.py
│   ├── utils.py
│   ├── validators.py
│   └── writer.py
├── announcements.qmd
├── faq.qmd
├── index.qmd
├── practicalities.qmd
├── preparation.qmd
├── resources.qmd
├── schedule.qmd
├── syllabus.qmd
├── team.qmd
├── _quarto.yml
├── styles.css
└── README.md
```

`docs/template_spec.md` is this specification. `_generated/` and `_site/` are build outputs; edit their source data, renderer, or authored page instead of editing generated output. The repository may also contain additional assets and configuration files not shown above.

## 3. Data files

| Data file | Purpose | Required? |
|---|---|---|
| `course.yml` | Core training identity and metadata used by the website | Yes |
| `website.yml` | Website configuration, page metadata, content-section definitions, welcome and footer settings | Yes |
| `schedule.yml` | Scheduled events | Optional in content; keep the file and use `events: []` when there are no events |
| `team.yml` | People, roles, and contact information | Required by the current renderer |
| `preparation.yml` | Preparation information and sections | Optional |
| `practicalities.yml` | Practical and logistical information | Optional |
| `faq.yml` | Frequently asked questions | Optional |
| `resources.yml` | Additional resources | Optional |
| `announcements.yml` | Homepage announcements | Keep the file; it may contain no announcements |

The current loaders open the YAML files by filename; they do not generally treat a missing file as equivalent to an empty optional file. In this table, “Optional” means that the corresponding page/content can be empty or unavailable, not that the YAML file can necessarily be deleted. Keep the data files in the repository and use an empty list/mapping where appropriate. In particular, an empty `announcements.yml` is handled as empty data, but a missing file is not handled as an optional-file case.

### 3.1 Single source of truth

Use the relevant YAML file as the source for structured information. Do not duplicate values in page markup when a renderer already reads them from YAML.

Some page text is intentionally authored directly in `.qmd` files. For example, the welcome text is edited in the welcome section, while the welcome title, dates, location, and image settings are supplied through data/configuration.

## 4. Page availability and navigation

The website uses `available_pages` calculated by `render_course.py` to decide which optional pages are available to the navbar. This is the central availability set for navbar generation; it is not controlled by boolean `website.pages.*` flags.

### 4.1 Page availability

| Page | Current availability rule |
|---|---|
| Overview | Always present |
| Content | Always present |
| Syllabus | Always present |
| Team | Always present in the navbar |
| Schedule | Available when the schedule contains events |
| Practical information | Available when practicalities data is truthy |
| Preparation | Available when `preparation.yml` has a `sections` value |
| FAQ | Available when FAQ data is truthy |
| Resources | Available when resources data is truthy |
| Announcements | Available when `announcements.yml` contains items |

The Team page is treated as always available by the navbar renderer. The team renderer also validates that team data contains members and at least one contact; therefore `team.yml` must be configured for a successful render.

### 4.2 Main navbar

The navbar has the following structure:

- Overview — always
- Content — always
- Schedule — when available
- Information dropdown (the label is hard-coded in the navbar renderer):
  - Preparation — when available
  - Practicalities — when available
  - Announcements — when available
  - Resources — when available
  - Team — always
  - Syllabus — always
  - FAQ — when available

The navbar and quick links do not use identical rules. Navbar availability is based on `available_pages`. Quick links additionally check whether the corresponding `.qmd` page exists and has non-empty content.

### 4.3 Optional page files

Do not assume that deleting an optional `.qmd` file alone removes its navbar item. Navbar availability is determined by data checks in `render_course.py`. The quick-links renderer separately checks page-file existence and content.

Keep the page metadata entries in `website.yml` for the keys used by the quick-links renderer. It indexes those entries directly, so omitting expected keys can cause a rendering error.

## 5. Homepage sections

The homepage is assembled in `index.qmd` by including sections. Inclusion in the page and whether a section has visible content are separate concerns.

### 5.1 Welcome

The welcome section is generated by `render_welcome(course, website)`.

- The training title, dates, and location come from `course.yml`.
- Start and end dates are displayed when available; if only one is available, only that date is shown. If neither is available, date metadata is omitted.
- Location is displayed when provided and omitted otherwise.
- The welcome heading, welcome text, and image settings come from the `welcome` section of `website.yml`.
- The image is displayed only when an image source is provided; its alt text is read from the same configuration.

The YAML data is the source of truth for the entire welcome section.

### 5.2 Registration banner

The registration section is included on the homepage, but the renderer may return no visible banner.

| Configuration/state | Result |
|---|---|
| `enabled: false` | No banner |
| Enabled but no `opening_date` | No banner |
| Before `opening_date` | “Registration opens soon” with the opening date |
| On/after opening and before or on closing date | Registration is open, provided `url` is set |
| Registration open but no `url` | No banner |
| After closing date, `after_closing: "closed"` | Closed message |
| After closing date, `after_closing: "hide"` or omitted | No banner |

If no closing date is provided, registration remains open after the opening date. While registration is open, the URL is required for the banner to appear.

Dates use `YYYY-MM-DD`.

Cost information:
- A fixed fee is displayed when both `cost.amount` and `cost.currency` are provided.
- `cost.note` can be displayed independently, for example to explain variable fees or funding arrangements.
- A note without an amount and currency does not create a fixed-fee display.

The renderer defaults `after_closing` to `hide`. Values other than `hide` produce the closed state in the current implementation; use the documented values `closed` and `hide`.

### 5.3 Upcoming

#### Behaviour

- If the schedule has no events, the Upcoming renderer returns an empty string and the section is omitted.
- If events exist, the Upcoming section is generated and its event data is passed to the page JavaScript.
- An event with a `content` reference can link to its corresponding content page.
- Content references ending in `.qmd` are converted to `.html`.

The section is data-driven: the current renderer does not read a `homepage.upcoming` setting. `schedule.js` selects the first event in the supplied event list whose end time is later than the current time. An event remains displayed while it is in progress; after it ends, the next qualifying event is shown. The countdown indicates time until the event starts, or time until it ends while it is in progress. The event list should therefore be kept in chronological order.

### 5.4 Quick links

The quick-links renderer selects cards in this priority order and displays no more than four:

1. Content
2. Syllabus
3. Schedule
4. Practical information
5. Preparation
6. Resources
7. FAQ

Content and Syllabus are always eligible. Schedule is eligible when events exist. Other optional cards are eligible when the corresponding page file exists and contains non-frontmatter content.

Because the maximum is four cards, lower-priority cards may not appear even when their pages are available. Announcements and Team are not in the quick-links priority list.

### 5.5 Announcements

The announcements section is included on the homepage.

- Announcements are read from `data/announcements.yml`.
- When items exist, the renderer sorts them newest first and displays up to two.
- When no items exist, the homepage section displays: **“No active announcements.”**
- Announcements are sorted newest first; the homepage displays up to two.
- The separate Announcements page displays all items and has its own empty state (“There are currently no announcements.”).
- The `website.homepage.announcements` flag is not used by the current renderer.
- The navbar includes Announcements only when `announcements.items` is non-empty.

### 5.6 Team preview

The homepage includes a team preview.

- It displays up to two people.
- Training leads are selected first; instructors fill any remaining preview places.
- Contributors are not shown in the homepage preview.
- The full Team page displays team members and their available profile information.

The team validator requires a non-empty members list and at least one contact. Do not treat `team.yml` as optional for the current build.

### 5.7 Footer

The footer container is always rendered.

- Organisation and licence information appear when provided.
- Licence text links only when a licence URL is provided.
- Template attribution is rendered from the `built_with` configuration.
- The repository link/icon is rendered only when both repository URL and image are provided.

## 6. Schedule

`schedule.yml` contains an `events` list. Use:

```yaml
events: []
```

when there are no scheduled events.

### 6.1 Event fields

The schedule renderer expects event records with `title`, `type`, `group`, `start`, `end`, `location`, and `people`. These fields are accessed directly, including `group`, `location`, and `people`; include them in each event. `description` is not displayed by the current schedule renderer.

```yaml
events:
  - title: "Example session"
    type: workshop
    group: "Day 1"
    start: "2026-10-12T09:00:00"
    end: "2026-10-12T10:00:00"
    location: "Room 1"
    people:
      - "Name"
    content: "content/module-1/introduction.qmd"
```

The top-level schedule validator checks only that the loaded value is a list; it does not validate event fields or event type. `content` is optional. When provided, it links the event title to the corresponding content page; `.qmd` is converted to `.html`.

The current renderer displays event times and does not use an `all_day` field.

### 6.2 Event types

The renderer uses event type values for the event's type label and CSS class. The types currently styled by the repository are:

- `lecture`
- `workshop`
- `practical`
- `discussion`
- `break`
- `welcome`
- `lunch`
- `presentation`
- `assessment`
- `group-work`
- `exercise`
- `consultation`
- `quiz`
- `feedback`
- `seminar`

This is a list of types styled in the current repository, not a validation-enforced enum.

### 6.3 Grouping and ordering

The schedule renderer sorts events by `start`, then groups them using each event's `group` value. The `group` field is accessed directly by the renderer, so it is required by the current implementation; it is not an optional field with an automatic date-based fallback.

Use a consistent group value for events that should appear together. Examples include:

- `Day 1`
- `Workshop Day 1`
- `Week 1`
- `Module 1`

Each group is shown with its group label and the date of its first event. Groups appear in the order in which their first event occurs after sorting.

For example:

```yaml
events:
  - title: "Introduction"
    type: lecture
    group: "Day 1"
    start: "2026-10-12T09:00:00"
    end: "2026-10-12T10:00:00"
    location: "Room 1"
    people: []
  - title: "Hands-on session"
    type: practical
    group: "Day 1"
    start: "2026-10-12T10:15:00"
    end: "2026-10-12T12:00:00"
    location: "Room 1"
    people: []
```

## 7. Content organization

The `content/` directory contains the learning material. Unlike the YAML configuration, the content structure is intentionally flexible: the template does not prescribe a pedagogical sequence or require authors to organize material into modules.

Recommendations:

- Keep `content/index.qmd` as the landing page for the learning material.
- Organize additional pages in a way that makes sense for the training.
- Use Quarto links or cross-references to guide learners between pages.
- Group related pages into folders when the material benefits from it.

A training may be organized by modules, days, units, parts, lectures, practicals, assignments, topics, or another structure appropriate to its content.

The top-level `content` configuration in `website.yml` defines the content sections. Each section has:

- `id` — machine-readable identifier and folder name
- `label` — short label shown in the content navigation/overview
- `title` — human-readable title used as a tooltip/title attribute

Example:

```yaml
content:
  sections:
    - id: module-1
      label: "Module 1"
      title: "Introduction to Open Science"
    - id: module-2
      label: "Module 2"
      title: "Research Data Management"
```

The section ID determines the folder under `content/`. The folder name must match the ID exactly. The course author chooses the section structure; sections may represent modules, days, units, parts, or another useful grouping.

### 7.1 Section ID conventions

- IDs must be unique within the content configuration.
- Use lowercase.
- Do not use spaces.
- Hyphens are recommended for readability.
- Keep IDs stable once the site is published, because links and references may depend on them.

The loader checks that the directory for each configured section exists and reads its `.qmd` pages. The current implementation does not validate the suggested lowercase/hyphen ID conventions; they are recommendations for maintainability.

### 7.2 Page ordering

Pages inside a section are `.qmd` files.

- Every `.qmd` page in a configured section must have a `title` in its frontmatter; the content loader raises an error if it is missing.
- `order` in page frontmatter can be used to control page ordering.
- If any page in a section has `order`, every page in that section must have it; mixing ordered and unordered pages raises an error.
- If no page has `order`, pages are sorted alphabetically by filename (case-insensitive).
- Ordering is evaluated independently within each section.

Example structure:

```text
content/
  index.qmd
  module-1/
    01-introduction.qmd
    02-open-principles.qmd
  module-2/
    01-data-management.qmd
    02-data-sharing.qmd
```

## 8. Syllabus

The Syllabus page is generated from `course.yml` and `team.yml` and is always included in the website navigation.

### 8.1 Required course fields

`validate_course()` currently requires:

- `course.title`
- `course.description`
- `course.mode`
- `course.language`
- `course.target_audience`
- `course.learning_outcomes` — a non-empty list
- `course.organizers` — a non-empty list
- `course.contact` — a mapping containing `email`

The validator does not currently enforce all fields displayed or potentially used by the syllabus renderer.

### 8.2 Optional displayed information

The syllabus renderer conditionally displays available values such as:

- Subtitle
- Start and end dates (either or both)
- Duration, delivery mode, location, and language
- Credits (`value`, optional `unit`, and optional `note`)
- Learning outcomes
- Target audience and expertise level
- Prerequisites
- Topics
- Organisers/team information
- Contact information
- Reuse/licence information

The exact fields used are determined by `render_syllabus()` and the current `course.yml` structure. Keep this section synchronized with that renderer and `validate_course()` when the schema changes.

## 9. Team data and pages

`team.yml` contains people associated with the training.

Common profile fields include:

| Field | Purpose |
|---|---|
| `name` | Person's name |
| `roles` | Role or roles in the training |
| `job_title` | Professional title |
| `affiliation` | Workplace or institution |
| `email` | Email contact |
| `orcid` | ORCID profile |
| `linkedin` | LinkedIn profile |
| `github` | GitHub profile |
| `website` | Personal or institutional webpage |
| `image` | Profile image |

The validator requires at least one member. Every member must have `name`, `roles` (a non-empty list), and `affiliation`. Allowed roles are exactly `Training lead`, `Instructor`, and `Contributor`. At least one member must have `course_contact: true` and a non-empty `email`; a contact flag without an email is an error.

The homepage preview displays up to two people: training leads first, then instructors to fill any remaining places. Contributors are not included in the preview. The full Team page groups people by the three supported roles and displays available profile information. Optional fields include `job_title`, `email`, `course_contact`, `bio`, `orcid`, `linkedin`, `github`, `website`, and `image`.

## 10. Practical information

Practical information is available when the practicalities data passes the current availability check. The renderer/page displays the configured practical information; empty or absent data does not create a useful page.

The current `practicalities.yml` structure supports:

- `intro`
- `venue`: `name`, `address`, `room`, `instructions`, `map_url`
- `transport`: `description`, `links`, `parking`
- `accommodation`: `description`, `hotels` (including `name`, `distance`, `walking_time`, and `url`)
- `food`: `description`, `dietary_information`
- `additional`: a list of titled `content` entries

The renderer displays a section only when it has relevant content. It can convert an OpenStreetMap share URL into an embedded map. For a venue map link, open the venue in OpenStreetMap, choose **Share**, enable **Include marker** if available, and use the resulting URL as `venue.map_url`.

## 11. Preparation information

Preparation is available when `preparation.yml` contains a `sections` value. The preparation page is built from the configured sections/blocks.

The preparation renderer supports these block types:

| Block type | Intended use |
|---|---|
| `text` | General explanatory content |
| `checklist` | Tasks participants should complete |
| `account` | Accounts participants need to create or access |
| `hardware` | Computer or equipment requirements |
| `software` | Software installation and setup |
| `reading` | Required or recommended reading |
| `callout` | Additional information; set `style` to `important`, `note`, or `warning` |

A preparation page is available when `preparation.sections` is non-empty. Each section has a `title` and `blocks`. Empty blocks and sections with no rendered blocks are omitted. Consecutive `account` blocks and consecutive `software` blocks are rendered in grids. Unknown block types are ignored by the renderer.

## 12. Other optional information pages

### FAQ

FAQ availability is based on whether FAQ data is truthy. The page content is generated from `faq.yml`.

### Resources

Resources availability is based on whether resources data is truthy. The page content is generated from `resources.yml`.

### Announcements

Announcements are generated from `announcements.yml`; the homepage section remains present even when the item list is empty.


## 13. Rendering architecture

The template separates **configuration**, **data processing**, **page composition**, and **presentation**. This lets training authors update structured information without manually editing every place where it appears.

### 13.1 Responsibilities by layer

| Layer | Responsibility |
|---|---|
| `data/*.yml` | Structured training, website, schedule, team, and optional-page data |
| `scripts/loaders.py` | Loads YAML files from `data/` |
| `scripts/validators.py` | Checks course, website, schedule-list, and team data |
| `scripts/render_course.py` | Coordinates loading, validation, availability checks, and renderer calls |
| `scripts/renderers/` | Converts structured data into reusable Quarto fragments or page content |
| Authored `.qmd` files | Compose pages and contain content maintained as Quarto |
| `styles.css` | Site-wide visual styling and responsive presentation |
| `js/schedule.js` | Browser-side Upcoming behaviour and schedule interactions |

Validation is not equally comprehensive for every data file. For example, the schedule validator checks only that the events value is a list; it does not validate individual event fields or event types.

### 13.2 Render flow

The website is rendered as part of the Quarto build process:

1. `quarto render` starts.
2. Quarto runs the configured pre-render step.
3. `scripts/render_course.py` deletes and recreates `_generated/`.
4. The renderer loads course, website, content, schedule, team, announcements, practicalities, FAQ, preparation, and resources data.
5. It validates course, website, schedule, and team data, then calculates `available_pages`.
6. Individual renderers generate Quarto/HTML fragments in `_generated/`.
7. Authored `.qmd` pages include or compose the generated fragments.
8. Quarto renders the site into `_site/`.

The main data-to-output relationship is:

```text
data/*.yml + content/
        │
        ▼
scripts/loaders.py + scripts/content.py
        │
        ▼
scripts/validators.py
        │
        ▼
scripts/render_course.py
        │
        ▼
scripts/renderers/
        │
        ▼
_generated/*
        │
        ▼
authored .qmd pages + _sections/
        │
        ▼
Quarto
        │
        ▼
_site/
```

`styles.css` and JavaScript support the rendered site at the presentation and browser-interaction layers.

### 13.3 Generated files

Files in `_generated/` are build artifacts. `render_course.py` removes and recreates the directory at the start of each run. Do not edit generated files manually; update the source YAML, Python renderer, or authored page instead.

`_site/` contains rendered website output and is not the source location for website content.

## 14. Behavioural summary

| Feature | Source of behaviour |
|---|---|
| Navbar optional links | `available_pages` in `render_course.py` and navbar renderer |
| Quick-link cards | `render_quick_links.py`; page content and event availability |
| Welcome metadata | `course.yml` and `website.yml`; welcome renderer |
| Registration banner | Registration settings in `website.yml`; registration renderer |
| Upcoming section | `schedule.yml`; upcoming renderer |
| Announcements | `announcements.yml`; announcements renderer |
| Team preview | `team.yml`; team renderer |
| Schedule page | `schedule.yml`; schedule renderer and page composition |
| Content section structure | Top-level `content.sections` in `website.yml` and `content/` folders |
| Footer | Footer settings in `website.yml`; footer renderer |

## 15. Keeping this specification current

When changing the repository, update this document if the change affects:

- YAML field names or requiredness
- Page availability rules
- Navbar or quick-link behaviour
- Homepage section visibility
- Renderer inputs or outputs
- Supported schedule event types
- Content-section or page-ordering rules

For exact behaviour, the implementation in `scripts/`, `scripts/renderers/`, and the authored `.qmd` files is authoritative.
