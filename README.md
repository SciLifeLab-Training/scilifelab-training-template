# SciLifeLab Training Webpage Template

The SciLifeLab Training Webpage Template is a Quarto-based template for
creating, publishing and maintaining FAIR, reusable training websites
with GitHub Pages.

The published template is available at:

**[SciLifeLab Training Webpage Template](https://scilifelab-training.github.io/scilifelab-training-template/)**

The template provides:

- a landing page with general information about a training, on the
  `main` branch;
- separate training instances, each maintained in a `release-YYMM`
  branch;
- automated publication of the landing page and training instances
  through GitHub Pages;
- citation, archiving and discovery metadata (`CITATION.cff`,
  `.zenodo.json` and Bioschemas) generated from the same data files.

> [!IMPORTANT]
> **On every branch, you only edit three things:**
>
> 1. **`data/`**: the information about the training.
> 2. **`content/`** (training instances only): the training materials.
> 3. **`README.md`**: a few short sections, after replacing this README
>    with the [README template](docs/_template-README.md).
>
> Everything else (the website layout, styling and scripts) works as it
> is. `CITATION.cff` and `.zenodo.json` are generated automatically from
> the data files: do not edit them by hand.

## User Guide

New to the template? See the **[SciLifeLab Training Webpage Template User Guide](https://scilifelab-training.github.io/scilifelab-training-template-user-guide/)**.

The User Guide provides step-by-step instructions for:

- creating your own copy of the template and preview it on your computer;
- setting up the landing page;
- creating a training instance and add your materials;
- preparing your training materials for publication, citation, and reuse following FAIR principles.

## Setting up the landing page

The landing page is built from four data files:

| File | Contents |
|---|---|
| `data/course.yml` | title, description, learning outcomes, keywords, topics, licence and DOI of the training |
| `data/team.yml` | the founders and contributors of the training |
| `data/website.yml` | logos, button labels, banner image and footer |
| `data/instances.yml` | the training instances, and which one is current |

When you start using the template for your own training:

1. In `data/website.yml`, set `template: false`. This removes the
   template banner, and makes `CITATION.cff`, `.zenodo.json` and the
   README describe your training instead of the template.
2. Replace this README with the [README template](docs/_template-README.md):
   copy the contents of `docs/_template-README.md` over `README.md`.
3. Fill in the data files.
4. Push to `main`. GitHub Actions renders the landing page, updates the
   generated files, and publishes the landing page.

You can then delete the `_template/` folder: it contains the citation
information of the template itself, which is only used while
`template` is `true`.

## Working locally

The website is built with [Quarto](https://quarto.org/).

After cloning the repository, create and activate the Python virtual
environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Render the site with:

```bash
quarto render
```

Or preview it locally with:

```bash
quarto preview
```

Rendering locally also updates the generated files.

## Development and maintenance

Technical documentation for developers and maintainers of the template
is available in [`docs/developer/`](docs/developer/). This includes the
landing page architecture, validation, generated files and deployment.

<!-- generated:contributors -->
## Contributors

| Name | Role | ORCID | Affiliation |
|------|------|-------|-------------|
| Ineke Luijten | Founder | [0000-0001-5768-275X](https://orcid.org/0000-0001-5768-275X) | SciLifeLab Training Hub |
| Nina Norgren | Founder | [0000-0002-3823-1555](https://orcid.org/0000-0002-3823-1555) | SciLifeLab Training Hub |
| Dimitris Panouris | Founder | [0009-0005-2282-2982](https://orcid.org/0009-0005-2282-2982) | SciLifeLab Training Hub |
<!-- /generated:contributors -->

## Contributing to the template

We welcome feedback and contributions to the template itself, such as
bug reports, ideas for new features, and improvements to the layout,
scripts or documentation.

- **Report a problem or suggest an improvement:** open an issue in the
  [template repository](https://github.com/SciLifeLab-Training/scilifelab-training-template/issues).
- **Propose a change:** fork the
  [template repository](https://github.com/SciLifeLab-Training/scilifelab-training-template)
  and open a pull request. Changes to the landing page go to `main`,
  and changes to the training instance pages go to `release-0000`.

The [CONTRIBUTING.md](CONTRIBUTING.md) file in this repository is part
of the template: it explains how to contribute to a **training** made
with the template, not to the template itself.

<!-- generated:citation -->
## Citation

If you use this software, please cite it as:

> Luijten, I.; Norgren, N.; Panouris, D. SciLifeLab Training Webpage Template. Version 1.0.0-alpha. https://scilifelab-training.github.io/scilifelab-training-template/

Citation metadata is available in [CITATION.cff](CITATION.cff).
<!-- /generated:citation -->

## Licence

Unless otherwise stated, the SciLifeLab Training Webpage Template is
licensed under the
[Creative Commons Attribution 4.0 International (CC BY 4.0) licence](https://creativecommons.org/licenses/by/4.0/).
