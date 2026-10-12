# Landing Migration Map

This document records how earlier landing page models map to the current data-driven architecture. The landing page has gone through three models:

1. **Legacy:** all content in `data/landing.yml`.
2. **Quarto-first:** static content written directly in `_sections/*.qmd`, with only the instance links generated from `data/instances.yml` and `data/ui.yml`.
3. **Data-driven (current):** all content in `data/*.yml`, with the same data model as the training instance branches. `_sections/*.qmd` are only shells that include generated fragments.

It is retained as a reference for developers maintaining or migrating the template. For the current architecture, validation and deployment model, see the [Landing Page Maintenance Runbook](landing-runbook.md).

## Quarto-first to data-driven

To migrate an existing landing page, copy the content of each authored section into the corresponding data field, then replace the `_sections/` files, `scripts/` and `index.qmd` with the current versions.

| Quarto-first source | Current source of truth | Notes |
|---|---|---|
| `_sections/hero.qmd` (`.hero__title`) | `data/course.yml` (`title`) | Also the page title and the title in all FAIR metadata |
| `_sections/hero.qmd` (`.hero__subtitle`) | `data/course.yml` (`subtitle`) | Also the meta description |
| `_sections/hero.qmd` (`.hero__brand` logo) | `data/website.yml` (`hero.logos`) | A list, so several logos are possible |
| `_sections/top-cards.qmd` (Training content) | `data/course.yml` (`description`) | Markdown; paragraphs separated by an empty line |
| `_sections/top-cards.qmd` (Learning outcomes) | `data/course.yml` (`learning_outcomes`) | Numbered automatically |
| `_sections/top-cards.qmd` (Keywords) | `data/course.yml` (`keywords`) | Required |
| `_sections/top-cards.qmd` (Topics covered) | `data/course.yml` (`topics`) | Optional; the card is left out when empty |
| `_sections/bottom-cards.qmd` (Founders) | `data/team.yml` (members with role `Founder`) | `given_names` and `family_names` |
| `_sections/bottom-cards.qmd` (Contributors) | `data/team.yml` (members with role `Contributor`) | |
| `_sections/instances-band.qmd` (decorative image) | `data/website.yml` (`instances_band.image`) | |
| `_sections/footer.qmd` | `data/website.yml` (`footer`) | Same structure as on the instance branches |
| `_sections/template-banner.qmd` | `data/website.yml` (`template`) | Shown only when `template: true` |
| `data/ui.yml` | `data/website.yml` (`labels`) | Same three keys; `ui.yml` is removed |
| Hand-written `CITATION.cff` | Generated from `data/` or, in template mode, `_template/` | Also `.zenodo.json`, README blocks and Bioschemas |

## Legacy to Quarto-first

| Legacy field | Quarto-first source of truth | Notes |
|---|---|---|
| `course.title` | `_sections/hero.qmd` (`.hero__title`) | Static authored copy. |
| `course.subtitle` | `_sections/hero.qmd` (`.hero__subtitle`) | Static authored copy. |
| `course.logo` | `_sections/hero.qmd` (`.hero__brand`) | Static authored asset reference. |
| `hero_actions[0].label` | `data/ui.yml` (`hero_view_current_label`) | Label for the current course instance button. |
| `hero_actions[0].href` | `data/instances.yml` current `instance_url` | Derived dynamically from the current instance; button is displayed when `show_in_hero: true`. |
| `hero_actions[0].style` | `scripts/generate_landing.py` template class (`hero-cta--primary`) | Presentation class is fixed in generator output. |
| `hero_actions[1].label` | `data/ui.yml` (`hero_registration_open_label`) | Label for the registration button. |
| `hero_actions[1].href` | `data/instances.yml` current `registration_url` | Derived dynamically from the current instance; button is omitted when `registration_url` is empty. |
| `hero_actions[1].style` | `scripts/generate_landing.py` template class (`hero-cta--secondary`) | Presentation class is fixed in generator output. |
| `instances.title` | `data/ui.yml` (`instances_band_title`) | Controls the heading in the *All course instances* banner. |
| `cards[*]` content | `_sections/top-cards.qmd` | Course content, learning outcomes, topics covered, and keywords are now authored directly in the card structure. |
| `founders[*]` | `_sections/bottom-cards.qmd` | Course founders are now authored directly in the card structure. |
| `contributors[*]` | `_sections/bottom-cards.qmd` | Course contributors are now authored directly in the card structure. |
| `footer.license` | `_sections/footer.qmd` (`.landing-footer__meta`) | Licence text and URL are authored directly in the footer. |
| `footer.built_with` | `_sections/footer.qmd` (`.landing-footer__meta`) | Hosting and build information is authored directly in the footer. |
| `footer.github_url` | `_sections/footer.qmd` (`.landing-footer__actions`) | Repository URL is set directly in the GitHub image link (`href`). |

### Elements added in the Quarto-first model

The current landing-page model includes elements and configuration options that did not have equivalent explicit keys in the legacy `data/landing.yml`.

#### `_sections/template-banner.qmd`

The template repository includes an onboarding banner that links to the externally maintained SciLifeLab Course Page Template User Guide.

This banner is specific to the template and is intended to be removed when the template is adapted for an individual course.

#### `data/ui.yml`

- `instances_band_title` — controls the title displayed in the *All course instances* banner.

#### `data/instances.yml`

- `show_in_hero` — controls whether the current course instance is displayed as an action button in the hero.
- `registration_url` — controls the registration link. If the value is empty, the registration button is not generated.

#### `_sections/instances-band.qmd`

The *All course instances* banner is divided between authored and generated content.

- `_sections/instances-band.qmd` contains the static banner structure and decorative image.
- `_generated/instances-band.qmd` contains the dynamically generated heading and course-instance links.

The generated content is created by `scripts/generate_landing.py` from `data/ui.yml` and `data/instances.yml`.

### Removed legacy file

`data/landing.yml` has been intentionally removed from the current architecture.

Its responsibilities are now divided between:

- `_sections/*.qmd` for authored landing-page content;
- `data/instances.yml` for course-instance configuration;
- `data/ui.yml` for configurable interface labels;
- `scripts/generate_landing.py` for validation and dynamic generation;
- `_generated/*.qmd` for generated landing-page fragments.

Files in `_generated/` are generated automatically and should not be edited manually.

In the data-driven model these sections and `data/ui.yml` were replaced in turn; see [Quarto-first to data-driven](#quarto-first-to-data-driven).
