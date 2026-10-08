# Contributing

Thank you for helping to improve this training. This guide explains how to
suggest changes to the training materials and the training website.

## Reporting a problem or suggesting an improvement

Open an issue in this repository. Describe what you found or what you would
like to change, and which training instance and page it concerns, for
example `release-2505`, Module 2.

## Making a change

1. Fork the repository, or create a branch if you have write access.
2. Make your change on the `release-YYMM` branch of the training instance it
   concerns.
3. Preview the website locally with `quarto render` and check the result in
   `_site/`.
4. Open a pull request against that `release-YYMM` branch, with a short
   description of the change.

Changes to the landing page go to `main` instead.

## What to edit

- **Training content**: the `.qmd` pages in `content/`. They are plain
  Markdown, so no knowledge of the website code is needed.
- **Training information**, such as the description, dates, learning
  outcomes, team and licence: the data files in `data/`.
- **Layout and styling**: the renderers and the CSS. Changes here affect
  every page, so please describe them clearly in the pull request.

Do not edit the generated files: `CITATION.cff`, `.zenodo.json`, the section
between the markers at the top of `README.md`, and anything in `_generated/`.
They are recreated from the data files on every render, so changes to them
are lost. Edit the data files instead.

## Credit

Contributors to the training materials are listed in `data/team.yml`. If you
contribute and would like to be credited, add yourself as a `Contributor` in
your pull request, or ask a training lead to add you. Everyone listed there
is included as an author in the citation and in the Zenodo record of the
next release, unless `citation_author: false` is set for them.

## Licence

By contributing, you agree that your contributions are made available under
the licence of this repository. See [LICENSE](LICENSE).
