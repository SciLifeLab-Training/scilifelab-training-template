# The SciLifeLab course template

The SciLifeLab template for setting up SciLifeLab branded courses using github pages. It includes:

- Pre-configured GitHub Actions for continuous deployment to GitHub Pages (works out-of-the-box within the SciLifeLab github organization).
- A github workflow for rendering the website and deploying it automatically.

## DISCLAIMER
This is the first version of this template, and can thus contain errors. Let us know if there are things that are broken.

## Getting Started

1. Click the **Use this template** button to create your own repository.
2. Rename the release-0000 branch to the year and month of your next course instance
3. (If outside the SciLifeLab organization) Set up your repository secrets so github actions can run.

## Configuration

- Modify the `_quarto.yml` file to configure branches to use. In this setup it's one branch per course instance, allowing you to keep older instances alive on the same website. Here is also where the menu items are listed. Push your changes.
- In the gh-pages branch, update the config file appropriately. This file will create a simple start page for all instances of the course.

## GitHub Actions

Your site will automatically build and deploy when you push changes. If you wish to customize the workflow, see `.github/workflows/main.yml`.
