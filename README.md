# SciLifeLab Training Webpage Template: training instance branch

This branch is the starting point for one **training instance**: one time a
training is given. It contains the training website (overview, schedule,
content and information pages), and is published to its own directory
on GitHub Pages.

> [!IMPORTANT]
> **To set up a training instance, you only edit three things:**
>
> 1. **`data/`**: the training information, such as the description,
>    dates, team and schedule.
> 2. **`content/`**: the training materials, one folder per module.
> 3. **`README.md`**: a few short sections, after replacing this README
>    with the [training README template](docs/_template-README.md).
>
> Everything else (the website layout, styling and scripts) works as it is.
> Files such as `CITATION.cff` and `.zenodo.json` are generated
> automatically from the data files: do not edit them by hand.

The landing page that lists all instances of a training lives on the
`main` branch, see [README on `main`](../../tree/main).

## User Guide

New to the template? See the **[SciLifeLab Training Webpage Template User Guide](https://scilifelab-training.github.io/scilifelab-training-template-user-guide/)**.

The User Guide provides step-by-step instructions for:

- setting up the template for a new training;
- customising the landing page;
- creating and managing training instances;
- customising training instance pages;
- previewing and publishing changes;
- preparing training materials for publication, citation, and reuse.

## Creating a new training instance

1. Create a new branch from this one and name it `release-YYMM`,
   for example `release-2705` for a training in May 2027.
2. Replace this README with the training README template:
   copy the contents of [`docs/_template-README.md`](docs/_template-README.md) over `README.md`.
3. Fill in the data files in `data/` and the content pages in `content/`.
4. Push the branch. GitHub Actions renders the website, updates the
   generated files, and publishes the website to `gh-pages/YYMM/`.
5. On the `main` branch, add the training instance to `data/instances.yml`, so the
   landing page links to it. Creating the branch does not do this
   automatically. 

The output directory is derived from the branch name, for example
`release-2705` is published to `gh-pages/2705/`.

## Files generated from the data files

Every render creates or updates these files from `data/course.yml`,
`data/team.yml` and `data/website.yml`:

| File | Purpose |
|---|---|
| `CITATION.cff` | citation metadata for GitHub and reference managers |
| `.zenodo.json` | metadata for the Zenodo record of each release |
| Bioschemas markup on the overview page | lets training registries such as ELIXIR TeSS find the training |
| The generated blocks in `README.md` | training information, contributors, citation and licence |

Do not edit these by hand: changes are overwritten on the next render.
Edit the data files instead.

## FAIRification: DOIs and Zenodo

Each training has one concept DOI, and every training instance is published
as a new version of it with its own version DOI.

1. **One-time setup:** a repository owner switches the repository on in
   the GitHub section of their Zenodo account.
2. Push the `release-YYMM` branch and wait for the workflow to finish.
3. On GitHub, create a release from that branch, with a tag such as
   `v2705`. Zenodo archives it and assigns a version DOI.
4. Add the DOIs and release date to `reuse` in `data/course.yml`:
   `doi` (the "Cite all versions" DOI, after the first release only),
   `version_doi` and `release_date`.

When you create a new instance from an existing one, empty
`version_doi` and `release_date`: they belong to the earlier instance.

Only create releases from `release-YYMM` branches, never from this
branch or from `main`.

## Working locally

The website is built with [Quarto](https://quarto.org/).

After cloning the repository, switch to the branch of the training
instance and create and activate the Python virtual environment:

```bash
git checkout release-YYMM
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Build the generated files once, then render or preview the site:

```bash
python scripts/render_course.py
quarto render     # or: quarto preview
```

## Development and maintenance

Technical documentation for developers and maintainers of the template is available in [`docs/_developer-SPEC.md`](docs/_developer-SPEC.md).

This includes documentation of the training instance-page architecture, validation and deployment.

## Contributors and citation

The SciLifeLab Training Webpage Template is developed and maintained by
the SciLifeLab Training Hub. See the [README on `main`](../../tree/main)
for the people behind the template, and how to cite it.

## Contributing to the template

We welcome feedback and contributions to the template itself, such as
bug reports, ideas for new features, and improvements to the layout,
scripts or documentation.

- **Report a problem or suggest an improvement:** open an issue in the
  [template repository](https://github.com/SciLifeLab-Training/scilifelab-training-template/issues).
- **Propose a change:** fork the
  [template repository](https://github.com/SciLifeLab-Training/scilifelab-training-template)
  and open a pull request. Changes to a specific training instance page go to
  `release-0000`, and changes to the landing page go to `main`.
  The [developer specification](docs/_developer-SPEC.md) describes how
  the template works.

The CONTRIBUTING.md file in this repository is part of the template: it explains how to contribute to a training made with the template, not to the template itself.

## Licence

Unless otherwise stated, the SciLifeLab Training Webpage Template is
licensed under the
[Creative Commons Attribution 4.0 International (CC BY 4.0) licence](https://creativecommons.org/licenses/by/4.0/).