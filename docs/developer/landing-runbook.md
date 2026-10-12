# Landing Page Maintenance Runbook

This document describes the technical architecture, data model, validation, generated files, FAIR metadata, deployment and recovery procedures for the landing page on the `main` branch.

It is intended for developers and maintainers of the SciLifeLab Training Webpage Template. Instructions for training organisers are provided in the [User Guide](https://scilifelab-training.github.io/scilifelab-course-webpage-template-user-guide/). The training instance branches are documented in `docs/_developer-SPEC.md` on the `release-0000` branch.

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

The landing page and training instances are deployed independently but share the same `gh-pages` branch.

> [!IMPORTANT]
> Do not edit `gh-pages` directly during normal development. It contains machine-managed published output. Manual changes should only be made as part of a targeted recovery procedure.

### 1.1 Design principles

The landing page follows the same principles as the training instance branches:

1. **One source of truth.** All landing page content lives in `data/*.yml`. Training organisers do not edit `.qmd` files.
2. **Separate data from presentation.** YAML describes information, Python renders it, Quarto composes the page, and `styles.css` styles it.
3. **FAIR by default.** `CITATION.cff`, `.zenodo.json`, the README blocks and the Bioschemas markup are generated from the same data as the page.
4. **One shared FAIR module.** `scripts/renderers/fair.py` is the same file on `main` and on the `release-YYMM` branches.

### 1.2 What training organisers edit

| What | Where |
|---|---|
| Training information: title, description, learning outcomes, keywords, topics, licence, DOI | `data/course.yml` |
| Founders and contributors | `data/team.yml` |
| Logos, button labels, banner image, footer, template mode | `data/website.yml` |
| Training instances, the current instance and registration links | `data/instances.yml` |
| Images | `img/` |
| A few hand-written README sections | `README.md`, based on `docs/_template-README.md` |

## 2. Repository structure

```text
main/
├── .github/workflows/
│   ├── deploy-landing.yml        # Landing deployment
│   └── validate-landing.yml      # Pull request checks
├── _generated/                   # Generated fragments (build output)
├── _sections/                    # Page section shells; include _generated/
├── _site/                        # Rendered website (build output)
├── _template/                    # Metadata of the template itself (template mode)
│   ├── course.yml
│   └── team.yml
├── data/
│   ├── course.yml
│   ├── instances.yml
│   ├── team.yml
│   └── website.yml
├── docs/
│   ├── _template-README.md       # README template for a training's main branch
│   └── developer/                # This runbook and the migration map
├── img/
├── scripts/
│   ├── generate_landing.py       # Pre-render entry point and validation
│   └── renderers/
│       ├── fair.py               # FAIR metadata (shared with release-YYMM)
│       ├── footer.py             # Footer (same as on release-YYMM)
│       └── landing.py            # Banner, hero, cards, instances band media
├── tests/
├── index.qmd
├── _quarto.yml
├── styles.css
├── requirements.txt              # Build dependencies
├── requirements-dev.txt          # Build and test dependencies
├── CITATION.cff                  # Generated
├── .zenodo.json                  # Generated
├── LICENSE.md
└── README.md                     # Partly generated
```

Only `index.qmd` is in the `render` list of `_quarto.yml`. Files and folders starting with `_` or `.` are never rendered by Quarto.

## 3. Render flow

1. `quarto render` starts and runs `scripts/generate_landing.py` as a pre-render step.
2. The generator loads and validates `data/instances.yml`, `data/course.yml`, `data/team.yml` and `data/website.yml`. Invalid data stops the render with an explanatory error.
3. Team members get a display `name` built from `given_names` and `family_names`.
4. `_generated/` is deleted and recreated.
5. The page fragments, the page metadata and the Bioschemas markup are written to `_generated/`.
6. `fair.py` writes `CITATION.cff` and `.zenodo.json`, and fills in the generated blocks of `README.md` (see [section 9](#9-fair-metadata)).
7. `index.qmd` includes the section shells in `_sections/`, which include the generated fragments.
8. Quarto renders the page to `_site/`.

```text
data/*.yml ──> generate_landing.py ──┬──> renderers/landing.py, footer.py ──> _generated/*.qmd ──┐
  (validation)                       │                                                         ├──> index.qmd ──> _site/
                                     ├──> renderers/fair.py ──> _generated/bioschemas.html ────┘
                                     │
_template/*.yml (template mode) ─────┴──> renderers/fair.py ──> CITATION.cff, .zenodo.json, README.md
```

### 3.1 Generated fragments

| Fragment | Source | Included by |
|---|---|---|
| `template-banner.qmd` | `website.template` | `_sections/template-banner.qmd` |
| `hero-brand.qmd` | `website.hero.logos` | `_sections/hero.qmd` |
| `hero-copy.qmd` | `course.title`, `course.subtitle` | `_sections/hero.qmd` |
| `hero-actions.qmd` | `instances.yml`, `website.labels` | `_sections/hero.qmd` |
| `top-cards.qmd` | `course.description`, `learning_outcomes`, `keywords`, `topics` | `_sections/top-cards.qmd` |
| `instances-band-media.qmd` | `website.instances_band.image` | `_sections/instances-band.qmd` |
| `instances-band.qmd` | `instances.yml`, `website.labels` | `_sections/instances-band.qmd` |
| `bottom-cards.qmd` | `team.yml` | `_sections/bottom-cards.qmd` |
| `footer.qmd` | `website.footer` | `_sections/footer.qmd` |
| `page-metadata.yml` | `course.title`, `course.subtitle` | `index.qmd` (`metadata-files`): browser tab title and meta description |
| `bioschemas.html` | `course.yml`, `team.yml`, `website.yml` | `index.qmd` (`include-in-header`) |

Do not edit files in `_generated/`. They are overwritten on every render.

The generated HTML uses the same classes as the original hand-written sections, so `styles.css` needs no changes. A card without content is left out: for example, the "Topics covered" card is not shown when `course.topics` is empty.

## 4. Data files

### 4.1 `data/course.yml`

| Field | Required | Used for |
|---|---|---|
| `title` | Yes | Hero, page title, README, citation, Zenodo, Bioschemas |
| `subtitle` | No | Hero, meta description, README |
| `description` | Yes | "Training content" card (Markdown), README, citation abstract, Zenodo, Bioschemas |
| `learning_outcomes` | Yes, non-empty list | "Learning outcomes" card, README, Bioschemas `teaches` |
| `keywords` | Yes, non-empty list | "Keywords" card, citation, Zenodo, Bioschemas (required by Bioschemas) |
| `topics` | No, list | "Topics covered" card |
| `language` | No | Zenodo (ISO 639-3), Bioschemas `inLanguage`, README |
| `target_audience`, `expertise_level` | No | README, Bioschemas |
| `organizers` | No, list | Bioschemas `provider` |
| `funding` | No, list | README, Zenodo, Bioschemas `funder` |
| `reuse.licence`, `reuse.licence_url`, `reuse.licence_id` | No | README, citation, Zenodo, Bioschemas |
| `reuse.doi` | No | The concept DOI of the training: README, citation, Bioschemas `@id` |
| `reuse.website_url`, `reuse.zenodo_communities`, `reuse.preferred_citation` | No | See [section 9](#9-fair-metadata) |

Use the same title, description, keywords and learning outcomes as on the `release-YYMM` branches, so the landing page and the instances describe the same training.

### 4.2 `data/team.yml`

| Field | Required | Notes |
|---|---|---|
| `given_names`, `family_names` | Yes | The display name is built from them |
| `roles` | Yes, non-empty list | `Founder` and/or `Contributor` |
| `affiliation` | Yes | |
| `orcid` | No | Full URL or bare ORCID; validated |
| `email`, `course_contact` | No | A course contact needs an email; listed as `contact` in `CITATION.cff` |
| `citation_author` | No | `false` leaves the person out of the citation; they become a Zenodo contributor instead |

Founders and contributors are shown in the two bottom cards. The instance roles (`Training lead`, `Instructor`) are not allowed on `main`.

### 4.3 `data/website.yml`

| Field | Notes |
|---|---|
| `template` | `true` in the template repository, `false` for a training (see [section 9.2](#92-template-mode)) |
| `hero.logos` | List of `src` and `alt` |
| `labels` | `hero_view_current_label`, `hero_registration_open_label`, `instances_band_title`. Unknown keys are an error; a missing label gets its default |
| `instances_band.image` | Decorative image of the "All training instances" banner |
| `footer` | Same structure as on the `release-YYMM` branches: `organisation`, `licence`, `built_with`, `repository` |
| `footer.repository.url` | Required; must be the GitHub address of the repository. Used to work out the website address |

### 4.4 `data/instances.yml`

The following rules are enforced:

- Exactly one instance must have `status: current`.
- The current instance must have `visible: true`.
- Each `slug` must be unique and contain four digits. `0000` is allowed as the template placeholder; other slugs must be a valid `YYMM` value.
- A relative `instance_url` must correspond to its slug, for example `slug: "2605"` with `instance_url: "./2605/"`.
- `registration_url` may be empty, relative, or use `http(s)`. Protocol-relative URLs such as `//example.org` are not allowed.
- `sort_key` must be an integer and not a boolean.

`visible` controls whether an instance is shown in the *All training instances* banner. For the current instance, `show_in_hero` controls whether it also gets a button in the hero.

## 5. Prerequisites and local setup

Local development requires Python 3.12 and Quarto 1.3.340 (matching the CI pin).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

In later terminal sessions, reactivate the environment with `source .venv/bin/activate`.

## 6. Local validation and rendering

Before pushing changes to `main`, run:

```bash
python -m pytest -q
quarto render
cffconvert --validate      # optional: pip install cffconvert
```

`quarto render` runs the generator, so it also updates `CITATION.cff`, `.zenodo.json` and `README.md`. Commit these files together with the data changes. To inspect the site, run `quarto preview`.

## 7. Validation

The generator stops the render with a message that explains how to fix the data:

- **`course.yml`:** `title` and `description` are required; `learning_outcomes` and `keywords` must be non-empty lists; `topics`, `organizers` and `funding` must be lists when given; `reuse.doi` and `reuse.version_doi` must be valid DOIs when given.
- **`team.yml`:** at least one member; every member needs a name, a non-empty list of allowed roles (`Founder`, `Contributor`) and an `affiliation`; `orcid` must be valid when given; a `course_contact` needs an email.
- **`website.yml`:** `template` must be `true` or `false`; each logo needs a `src`; `footer.repository.url` must be a GitHub repository address; `labels` may only contain the documented keys.
- **`instances.yml`:** see [section 4.4](#44-datainstancesyml).
- **`_template/`** (template mode only): `course.title` and `course.description` are required, and `team.yml` follows the same rules as `data/team.yml`.

## 8. Relationship between instances and the landing page

Training instance branches are not automatically discovered by the landing page. Creating and pushing `release-2605` publishes that instance, but does **not** add it to the landing page. Add it to `data/instances.yml` on `main`:

```yaml
- slug: "2605"
  label: "May 2026"
  status: current
  visible: true
  show_in_hero: true
  instance_url: "./2605/"
  registration_url: ""
  sort_key: 202605
```

## 9. FAIR metadata

All FAIR metadata is generated by `scripts/renderers/fair.py`, called with `scope="course"`. On the `release-YYMM` branches the same file is called with the default `scope="instance"`.

| Output | Location | Purpose |
|---|---|---|
| `CITATION.cff` | Repository root | Citation metadata. GitHub's "Cite this repository" reads it from `main` |
| `.zenodo.json` | Repository root | Zenodo metadata, used when a release is created from `main` |
| Bioschemas JSON-LD | `_generated/bioschemas.html`, in the `<head>` | Discovery by training registries such as ELIXIR TeSS |
| Generated README blocks | `README.md` | Training information for people browsing the repository |

Files are only rewritten when their content changes.

### 9.1 Course scope

Compared with a training instance:

| | `scope="course"` (`main`) | `scope="instance"` (`release-YYMM`) |
|---|---|---|
| Website | The landing page, `https://<owner>.github.io/<repo>/` | The instance website, `.../YYMM/` |
| Version | `reuse.version`, only when given | `reuse.version`, or the instance id |
| DOI | `reuse.version_doi`, or the concept DOI `reuse.doi` | The same |
| Bioschemas | The Course only, with `inLanguage` and `funder` | The Course with this CourseInstance |

The Course `@id` is the concept DOI (`https://doi.org/...`) when set, otherwise the landing page address with `#course`. It is the same on the landing page and on every instance page, so registries recognise all instances as runs of one training.

The README blocks are the same as on the instance branches (`header`, `course-information`, `learning-outcomes`, `contributors`, `citation`, `licence`, `acknowledgements`). A README without markers is never changed.

### 9.2 Template mode

In the template repository, `main` is both the template and an example landing page. `website.template` decides what the FAIR files describe:

| | `template: true` | `template: false` |
|---|---|---|
| Template banner on the landing page | Shown | Hidden |
| `CITATION.cff`, `.zenodo.json`, README blocks | The template, from `_template/course.yml` and `_template/team.yml` | The training, from `data/course.yml` and `data/team.yml` |
| Bioschemas markup | None (the page shows an example training) | The training, from `data/` |

`_template/course.yml` sets `reuse.upload_type: software`, so the template is archived on Zenodo as software and `CITATION.cff` uses the software citation message. Update `reuse.version` and `reuse.release_date` there before each template release.

A training that adopts the template sets `template: false`, copies `docs/_template-README.md` over `README.md`, and can delete `_template/`.

## 10. GitHub Actions

### Landing validation: `.github/workflows/validate-landing.yml`

- runs on pull requests to `main`;
- runs the tests;
- renders the landing page;
- validates the generated `CITATION.cff` with `cffconvert`;
- checks that raw YAML configuration does not leak into `_site`.

### Landing deployment: `.github/workflows/deploy-landing.yml`

- runs on pushes to `main`;
- renders the landing page;
- commits changed generated files (`CITATION.cff`, `.zenodo.json`, `README.md`) back to `main`. Commits pushed with the workflow token do not trigger a new run;
- publishes only landing-owned files and directories to `gh-pages`.

> [!IMPORTANT]
> If `main` is protected with a rule that blocks direct pushes, the "Commit generated metadata files" step fails. Either allow GitHub Actions to push to `main`, or remove the step and commit the generated files after rendering locally.

### Training instance deployment: `.github/workflows/main.yml`

On `release-*` branches, this workflow publishes the instance to its own directory on `gh-pages`, for example `release-2605 → gh-pages/2605/`. Updating an instance does not republish the landing page.

## 11. Deployment safety contract

The landing page and training instances share the same `gh-pages` branch. The landing deployment must:

- copy only landing-owned root files, including `index.html` and `styles.css`;
- mirror only landing-owned directories such as `site_libs/`, `index_files/` and `img/`, using per-directory deletion where required;
- never perform a root-level destructive sync such as `rsync -a --delete _site/ gh-pages/`;
- preserve `.nojekyll` on `gh-pages`;
- prevent raw configuration files from being published, and remove leaked configuration such as `gh-pages/data` or root YAML files;
- use the shared `deploy-gh-pages` concurrency group for landing and instance deployments.

## 12. Important maintenance rules

1. Treat `gh-pages` as machine-managed output.
2. Do not edit `_generated/*`, `CITATION.cff` or `.zenodo.json` manually.
3. Keep `scripts/renderers/fair.py` and `scripts/renderers/footer.py` identical on `main` and `release-0000`. When you change one, copy it to the other branch.
4. Keep raw YAML configuration out of the published site.
5. Preserve `.nojekyll` on `gh-pages`, and do not introduce a root-level destructive deployment sync.
6. Keep landing and instance deployments isolated.
7. Update `data/instances.yml` on `main` when instance visibility, status or links change.
8. Keep validation rules, the data file comments and this runbook aligned.

## 13. Deployment recovery

If a deployment assertion fails:

1. Identify and fix the workflow or configuration problem on `main`.
2. Re-run the failed validation or deployment.
3. If an incorrect artifact has already been written to `gh-pages`, remove only the affected artifact using a targeted cleanup commit.
4. Re-run the deployment from `main` to restore the expected landing page output.

Do not add a permanent assertion bypass to a workflow in order to make a failed deployment pass. If instance content has been affected, verify that the corresponding `gh-pages/YYMM/` directory remains intact before performing additional deployment operations.

If the "Commit generated metadata files" step fails because `main` changed in the meantime, re-run the workflow.

## 14. Related documentation

- [User Guide](https://scilifelab-training.github.io/scilifelab-course-webpage-template-user-guide/): instructions for training organisers.
- [`landing-migration-map.md`](landing-migration-map.md): how the earlier landing page models map to the current data files.
- `docs/_developer-SPEC.md` on `release-0000`: the training instance branches.
