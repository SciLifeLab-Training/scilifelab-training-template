# Contributing

Thank you for helping to improve this training. This guide explains how to
suggest changes to the landing page, training instance pages and training
materials.

## How this repository is organised

Each part of the training has its own branch:

| Branch | What it contains |
|---|---|
| `main` | The landing page: the general information about the training, and links to every training instance |
| `release-YYMM` | One training instance: the website and materials for one time the training is given. For example, `release-2705` is the training in May 2027 |

Make sure you report problems and make changes on the right branch!

## Reporting a problem or suggesting an improvement

Open an issue in this repository. Describe what you found or what you would
like to change, and where:

- for the landing page, say so;
- for a training instance, give its branch and page, for example
  `release-2705`, Module 2.

## Making a change

1. Fork the repository, or create a branch if you have write access.
2. Make your change on the branch it concerns: `main` for the landing page,
   or the `release-YYMM` branch of the training instance.
3. Preview the website locally with `python scripts/preview.py`, and check
   the result in your browser.
4. Open a pull request against that same branch, with a short description
   of the change.

## What to edit

- **Training information**, such as the title, description, learning
  outcomes, team and licence: the data files in `data/`. On `main`, these
  describe the training as a whole; on a `release-YYMM` branch, that one
  training instance, including its dates and schedule.
- **Training materials** (`release-YYMM` branches only): the `.qmd` pages
  in `content/`. They are plain Markdown, so no knowledge of the website
  code is needed.
- **Images and logos**: the files in `img/`.
- **Layout and styling**: the scripts and the CSS. Changes here affect
  every page, so please describe them clearly in the pull request.

Do not edit the generated files: `CITATION.cff`, `.zenodo.json`, the parts of
`README.md` between `<!-- generated:... -->` markers, and anything in
`_generated/`. They are recreated from the data files every time the website
is rendered, so changes to them are lost. Edit the data files instead.

## Credit

The people behind the training are listed in `data/team.yml`:

- on `main`: the founders and contributors of the training as a whole;
- on a `release-YYMM` branch: the team of that training instance.

If you contribute and would like to be credited, add yourself to the
`data/team.yml` of the branch you changed, or ask the team to add you.
Everyone listed there is included as an author in the citation and in the
Zenodo record, unless `citation_author: false` is set for them.

## Licence

By contributing, you agree that your contributions are made available under
the licence of this repository. See [LICENSE](LICENSE.md).