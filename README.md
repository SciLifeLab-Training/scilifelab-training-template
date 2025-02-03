# The SciLifeLab course template

The SciLifeLab template for setting up SciLifeLab branded courses using github pages. It includes:

- Pre-configured GitHub Actions for continuous deployment to GitHub Pages (works out-of-the-box within the SciLifeLab github organization).
- A github workflow for rendering the website and deploying it automatically.
- All pages are rendered using Quarto. For customizations see the official Quarto documentation. While developing the materials you can use quarto to render the pages locally.

You can see how this template looks when rendered at [https://scilifelab-training.github.io/scilifelab-training-template/](https://scilifelab-training.github.io/scilifelab-training-template/). 

## DISCLAIMER
This is the first version of this template, and can thus contain errors. Let us know if there are things that are broken.

## Getting Started

1. Click the **Use this template** button to create your own repository.
2. The template does not copy all branches from the template, these you have to copy over from the template yourself:
   - Create an empty branch called gh-pages. Copy the file called `_config.yml` from the template repo into it, and change the content accordingly.
3. (If outside the SciLifeLab organization) Set up your repository secrets so github actions can run. If you name it ORG_PAT it will work without changing the workflow file.
4. Github actions will run when you push, but before everything is setup it will fail in running correctly. Once everything is set up correctly this should be solved automatically.

## Configuration

- Modify the `_quarto.yml` file to configure branches to use. In this setup it's one branch per course instance, allowing you to keep older instances alive on the same website. Name your branch release-* (YYMM). Here is also where the menu items are listed. Push your changes.
- Create and push the new branch from the main branch.

## GitHub Actions

Your site will automatically build and deploy when you push changes. If you wish to customize the workflow, see `.github/workflows/main.yml`. See Actions in github to see where your page is deployed.
