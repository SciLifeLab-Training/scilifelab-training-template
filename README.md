<!-- training-info:start -->
<!-- This section is generated automatically from the data files in data/. Edit the data files instead; text outside the markers is kept. -->

# Training title

*Short subtitle describing the training.*

Provide a short description of the training, including its main topic, purpose, or focus.

- **Dates:** 2026-01-01 – 2026-01-02
- **Mode:** Online / In-person / Hybrid
- **Location:** Venue name or online
- **Language:** Language the training is provided in
- **Expertise level:** Beginner / Intermediate / Advanced
- **Website:** <https://your-organisation.github.io/your-repository/0000/>
- **DOI:** [10.5281/zenodo.20430336](https://doi.org/10.5281/zenodo.20430336)

## How to cite

Lastname1, F.; Lastname2, F.; Lastname3, F. Training title. Version 0000. https://doi.org/10.5281/zenodo.20430336

Citation metadata is available in [CITATION.cff](CITATION.cff).

## Licence

The training materials are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

<!-- training-info:end -->

## About this repository

This branch contains one instance of the training, built with the
[SciLifeLab Training Webpage Template](https://github.com/SciLifeLab-Training/scilifelab-training-template-staging).
Each `release-YYMM` branch publishes one training instance to `gh-pages/YYMM/`.
The landing page at the root of the site lives on `main`.

## Metadata and citation

The training metadata lives in the data files:

- `data/course.yml`: title, description, dates, learning outcomes, licence, DOI
- `data/team.yml`: the training team, used as the list of authors
- `data/website.yml`: repository URL and other website settings

From these, every render generates:

- `CITATION.cff`: citation metadata for GitHub and reference managers
- `.zenodo.json`: metadata for the Zenodo record of each release
- the "About this training" section at the top of this README
- Bioschemas markup on the overview page, so the training can be
  harvested by training registries such as ELIXIR TeSS

Do not edit these generated files by hand: changes are overwritten on the
next render. Edit the data files instead.

## DOIs and Zenodo

The training has one concept DOI, and every training instance is published
as a new version of it with its own version DOI. The concept DOI always
resolves to the latest instance.

One-time setup: a repository owner logs in to Zenodo, opens the GitHub
section of their Zenodo account, and switches on this repository.

To publish an instance to Zenodo:

1. Make sure the data files are complete, push the branch, and wait for the
   workflow to finish. It commits the updated `CITATION.cff` and
   `.zenodo.json` to the branch.
2. On GitHub, create a release from the `release-YYMM` branch, with a tag
   such as `v2505`. Zenodo archives the release and assigns a version DOI.
3. After the very first release, add the concept DOI to `reuse.doi` in
   `data/course.yml`. It stays the same for all later instances.
4. Optionally add this release's DOI to `reuse.version_doi` and its date to
   `reuse.release_date`, so the website, README and `CITATION.cff` cite this
   specific instance.

When you create a new instance from an existing one, clear
`reuse.version_doi` and `reuse.release_date` first: they belong to the
earlier instance.

Only create releases from `release-YYMM` branches. A release from `main`
would also become a version of the training on Zenodo.

## Creating a new instance

1. Create a new branch from `release-0000`.
2. Name it `release-YYMM`, for example `release-2505`.
3. Update the data files and course content in that new branch.
4. Push the branch.
5. GitHub Actions renders the training website, updates the generated
   metadata files on the branch, and publishes the website to the matching
   directory on `gh-pages`.

The output directory is derived from the branch name by the release workflow.
You do not need to maintain a separate branch-mapping list in `_quarto.yml`.

## What to edit

For normal course work, edit:

- the data files in `data/`
- the course `.qmd` pages
- `_quarto.yml` for course-site settings like title, sidebar, navbar, and theme
- images and other course assets

## Local preview

If you have Quarto installed, you can render locally:

```bash
quarto render
```

Rendered output is written to `_site/`. Rendering locally also updates the
generated metadata files.

## GitHub Actions

This branch uses `.github/workflows/main.yml`.

On push to a `release-*` branch, the workflow:

1. reads the branch name
2. validates that it matches `release-YYMM`
3. renders the course site
4. commits any changes to the generated metadata files back to the branch
5. publishes the result to the matching directory on `gh-pages`

Examples:

- `release-0000` -> `gh-pages/0000/`
- `release-2505` -> `gh-pages/2505/`

## Notes

- `gh-pages` is deployment output only
- `.nojekyll` is kept by the workflow
- the landing page branch (`main`) separately controls which instances appear
  on the landing page

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
